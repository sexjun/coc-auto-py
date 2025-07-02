import cv2
import numpy as np
import os
from adb_controller import ADBController
import time
from pathlib import Path


class TemplateMatcher:
    """
    子图匹配类，用于在手机屏幕截图中查找指定的模板图片
    依赖于ADBController类获取手机截图
    """

    def __init__(self, adb_controller=None):
        """
        初始化子图匹配器

        参数:
            adb_controller: ADBController实例，如果为None则自动创建一个
        """
        self.adb = adb_controller if adb_controller else ADBController()
        self.last_screenshot = None
        self.last_screenshot_path = None
        self.last_screenshot_time = 0

    def take_screenshot(
        self, force_new=False, save_path=Path(__file__).parent / "tmp_img_save_folder/screenshot.png"
    ):
        """
        获取手机屏幕截图

        参数:
            force_new: 是否强制获取新截图，否则可能返回缓存的截图(3秒内)
            save_path: 截图保存路径，默认为临时文件

        返回:
            numpy.ndarray: 截图的OpenCV格式图像对象
        """
        current_time = time.time()

        # 如果强制获取新截图或者缓存已过期(超过3秒)或者没有缓存
        if (
            force_new
            or current_time - self.last_screenshot_time > 3
            or self.last_screenshot is None
        ):

            # 使用ADB截图
            screenshot_path = self.adb.screenshot(save_path)
            self.last_screenshot_path = screenshot_path
            self.last_screenshot = cv2.imread(screenshot_path)
            self.last_screenshot_time = current_time

        return self.last_screenshot

    def find_template(
        self,
        template_path,
        threshold=0.8,
        method=cv2.TM_CCOEFF_NORMED,
        force_new_screenshot=False,
        debug_image=None,
    ):
        """
        在手机屏幕截图中查找模板图片

        参数:
            template_path: 模板图片路径
            threshold: 匹配阈值，0-1之间，越高要求越精确
            method: OpenCV模板匹配的方法
            force_new_screenshot: 是否强制获取新截图
            debug_image: 调试图像保存路径，如果为None则不保存

        返回:
            成功时返回元组 (center_x, center_y, confidence)，表示匹配位置的中心点坐标和置信度
            失败时返回 None
        """
        if not os.path.exists(template_path):
            print(f"错误: 模板图片不存在: {template_path}")
            return None

        # 读取模板图片
        template = cv2.imread(template_path)
        if template is None:
            print(f"错误: 无法读取模板图片: {template_path}")
            return None

        # 获取手机屏幕截图
        screenshot = self.take_screenshot(force_new=force_new_screenshot)
        if screenshot is None:
            print("错误: 无法获取手机屏幕截图")
            return None

        # 获取模板尺寸
        h, w = template.shape[:2]

        # 执行模板匹配
        result = cv2.matchTemplate(screenshot, template, method)

        # 获取最佳匹配位置和置信度
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # 根据所选方法确定最佳匹配位置
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            confidence = 1 - min_val  # 这些方法是越小越好
            match_loc = min_loc
        else:
            confidence = max_val  # 其他方法是越大越好
            match_loc = max_loc

        # 如果置信度低于阈值，认为匹配失败
        if confidence < threshold:
            print(
                f"未找到匹配，最高置信度: {confidence:.4f}, 阈值: {threshold}",
                template_path,
            )
            return None

        # 计算匹配区域的中心点
        center_x = match_loc[0] + w // 2
        center_y = match_loc[1] + h // 2

        # 如果需要，保存调试图像
        if debug_image:
            debug_img = screenshot.copy()
            # 绘制矩形框和中心点
            cv2.rectangle(
                debug_img,
                match_loc,
                (match_loc[0] + w, match_loc[1] + h),
                (0, 255, 0),
                2,
            )
            cv2.circle(debug_img, (center_x, center_y), 5, (0, 0, 255), -1)
            cv2.putText(
                debug_img,
                f"Conf: {confidence:.4f}",
                (match_loc[0], match_loc[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )
            cv2.imwrite(debug_image, debug_img)
            print(f"调试图像已保存到: {debug_image}")

        print(f"模板匹配成功: 中心点=({center_x}, {center_y}), 置信度={confidence:.4f}")
        return (center_x, center_y, confidence)

    def find_and_tap(
        self, template_path, threshold=0.8, force_new_screenshot=False, debug_image=None
    ):
        """
        查找模板图片并点击其中心点

        参数:
            template_path: 模板图片路径
            threshold: 匹配阈值
            force_new_screenshot: 是否强制获取新截图
            debug_image: 调试图像保存路径

        返回:
            成功时返回 True，失败时返回 False
        """
        result = self.find_template(
            template_path,
            threshold,
            force_new_screenshot=force_new_screenshot,
            debug_image=debug_image,
        )

        if result:
            center_x, center_y, _ = result
            # 使用ADB点击中心点
            tap_result = self.adb.tap(center_x, center_y)
            return tap_result
        else:
            return False

    def find_all_templates(
        self,
        template_path,
        threshold=0.8,
        method=cv2.TM_CCOEFF_NORMED,
        max_results=10,
        force_new_screenshot=False,
        debug_image=None,
    ):
        """
        在屏幕中查找所有匹配的模板实例

        参数:
            template_path: 模板图片路径
            threshold: 匹配阈值
            method: 匹配方法
            max_results: 最大结果数量
            force_new_screenshot: 是否强制获取新截图
            debug_image: 调试图像保存路径

        返回:
            列表，包含所有匹配的中心点坐标和置信度 [(x1, y1, conf1), (x2, y2, conf2), ...]
        """
        if not os.path.exists(template_path):
            print(f"错误: 模板图片不存在: {template_path}")
            return []

        # 读取模板图片
        template = cv2.imread(template_path)
        if template is None:
            print(f"错误: 无法读取模板图片: {template_path}")
            return []

        # 获取手机屏幕截图
        screenshot = self.take_screenshot(force_new=force_new_screenshot)
        if screenshot is None:
            print("错误: 无法获取手机屏幕截图")
            return []

        # 获取模板尺寸
        h, w = template.shape[:2]

        # 执行模板匹配
        result = cv2.matchTemplate(screenshot, template, method)

        # 准备调试图像
        debug_img = screenshot.copy() if debug_image else None

        matches = []

        # 迭代查找所有匹配
        for _ in range(max_results):
            # 获取最佳匹配位置
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            # 根据所选方法确定最佳匹配位置和置信度
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                confidence = 1 - min_val  # 这些方法是越小越好
                match_loc = min_loc
            else:
                confidence = max_val  # 其他方法是越大越好
                match_loc = max_loc

            # 如果置信度低于阈值，结束搜索
            if confidence < threshold:
                break

            # 计算匹配区域的中心点
            center_x = match_loc[0] + w // 2
            center_y = match_loc[1] + h // 2

            # 添加到结果列表
            matches.append((center_x, center_y, confidence))

            # 在结果图像中将已找到的区域填充，避免重复匹配
            cv2.rectangle(
                result,
                (match_loc[0] - w // 2, match_loc[1] - h // 2),
                (match_loc[0] + w // 2, match_loc[1] + h // 2),
                0,
                -1,
            )  # 将该区域填充为0

            # 如果需要，在调试图像上绘制匹配区域
            if debug_img is not None:
                cv2.rectangle(
                    debug_img,
                    match_loc,
                    (match_loc[0] + w, match_loc[1] + h),
                    (0, 255, 0),
                    2,
                )
                cv2.circle(debug_img, (center_x, center_y), 5, (0, 0, 255), -1)
                cv2.putText(
                    debug_img,
                    f"{len(matches)}: {confidence:.4f}",
                    (match_loc[0], match_loc[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2,
                )

        # 如果需要，保存调试图像
        if debug_image and debug_img is not None:
            cv2.imwrite(debug_image, debug_img)
            print(f"调试图像已保存到: {debug_image}")

        if matches:
            print(f"找到 {len(matches)} 个匹配")
        else:
            print("未找到匹配")

        return matches


# 使用示例
if __name__ == "__main__":
    try:
        # 创建ADB控制器和模板匹配器
        adb = ADBController()
        matcher = TemplateMatcher(adb)

        # 示例1: 查找单个模板
        template_path = "tmp_img_save_folder/templates/button.png"  # 替换为实际的模板图片路径
        result = matcher.find_template(
            template_path, threshold=0.7, debug_image="tmp_img_save_folder/debug_match.png"
        )

        if result:
            x, y, conf = result
            print(f"找到模板，中心点: ({x}, {y})，置信度: {conf:.4f}")

            # 点击匹配到的位置
            adb.tap(x, y)
        else:
            print("未找到模板")

        # 示例2: 查找和点击
        success = matcher.find_and_tap(
            "tmp_img_save_folder/templates/icon.png", threshold=0.7, debug_image="tmp_img_save_folder/debug_tap.png"
        )
        print(f"点击结果: {'成功' if success else '失败'}")

        # 示例3: 查找多个匹配
        matches = matcher.find_all_templates(
            "tmp_img_save_folder/templates/item.png",
            threshold=0.7,
            max_results=5,
            debug_image="tmp_img_save_folder/debug_multiple.png",
        )
        print(f"共找到 {len(matches)} 个匹配")

        # 点击所有匹配的位置
        for i, (x, y, conf) in enumerate(matches):
            print(f"点击第 {i+1} 个匹配，坐标: ({x}, {y})，置信度: {conf:.4f}")
            adb.tap(x, y)
            time.sleep(1)  # 间隔1秒点击下一个

    except Exception as e:
        print(f"错误: {str(e)}")
