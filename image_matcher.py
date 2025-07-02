import cv2
import numpy as np
import pyautogui
import argparse
from pathlib import Path


def match_image(
    template_path,
    threshold=0.8,
    scale_range=(0.5, 1.5),
    scale_step=0.05,
    find_all=False,
    max_results=10,
    save_debug=True,
    debug_path="./tmp_img_save_folder/debug_match.png",
):
    """
    简易包装函数，在屏幕中查找指定图像，并可选择保存调试图像

    参数:
        template_path: 要查找的模板图像路径（字符串或Path对象）
        threshold: 匹配阈值，0-1之间，值越高要求匹配度越高
        scale_range: 缩放范围的元组 (最小缩放, 最大缩放)
        scale_step: 缩放步长
        find_all: 是否查找所有匹配（True）或仅查找最佳匹配（False）
        max_results: 查找所有匹配时的最大结果数量
        save_debug: 是否保存调试图像
        debug_path: 调试图像保存路径

    返回:
        如果 find_all=False: 返回匹配位置的中心点坐标 (x, y) 或 None（未找到匹配）
        如果 find_all=True: 返回匹配位置中心点坐标列表 [(x1, y1), (x2, y2), ...] 或空列表（未找到匹配）
    """
    # 确保模板图像存在
    template_path = Path(template_path)
    if not template_path.exists():
        print(f"错误：找不到模板图像 {template_path}")
        return [] if find_all else None

    # 根据参数选择查找单个匹配或所有匹配
    if find_all:
        matches = find_all_matches(
            template_path,
            threshold=threshold,
            scale_range=scale_range,
            scale_step=scale_step,
            max_results=max_results,
        )
        result = matches
    else:
        match = find_image_in_screenshot(
            template_path,
            threshold=threshold,
            scale_range=scale_range,
            scale_step=scale_step,
        )
        result = match
        matches = [match] if match else []

    # 如果启用调试模式，保存调试图像
    if save_debug and matches:
        save_debug_image(template_path, matches, debug_path)

    return result


def find_image_in_screenshot(
    template_path, threshold=0.8, scale_range=(0.5, 1.5), scale_step=0.05
):
    """
    在屏幕截图中查找模板图像，支持不同缩放比例

    参数:
        template_path: 要查找的模板图像路径
        threshold: 匹配阈值，0-1之间，值越高要求匹配度越高
        scale_range: 缩放范围的元组 (最小缩放, 最大缩放)
        scale_step: 缩放步长

    返回:
        如果找到匹配，返回匹配位置的中心点坐标 (x, y)
        如果未找到匹配，返回 None
    """
    # 读取模板图像
    template = cv2.imread(str(template_path))
    if template is None:
        print(f"错误：无法读取模板图像 {template_path}")
        return None

    # 将模板转换为灰度图
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # 获取屏幕截图
    screenshot = pyautogui.screenshot()
    # 将PIL图像转换为OpenCV格式
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    # 转换为灰度图
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    best_match_val = -1
    best_match_loc = None
    best_scale = 1.0

    # 尝试不同的缩放比例
    current_scale = scale_range[0]
    while current_scale <= scale_range[1]:
        # 缩放模板
        scaled_template = cv2.resize(
            template_gray,
            None,
            fx=current_scale,
            fy=current_scale,
            interpolation=cv2.INTER_AREA if current_scale < 1 else cv2.INTER_LINEAR,
        )

        template_h, template_w = scaled_template.shape

        # 执行模板匹配
        result = cv2.matchTemplate(
            screenshot_gray, scaled_template, cv2.TM_CCOEFF_NORMED
        )

        # 查找最佳匹配位置
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # 如果找到更好的匹配
        if max_val > best_match_val:
            best_match_val = max_val
            best_match_loc = max_loc
            best_scale = current_scale

        current_scale += scale_step

    # 如果最佳匹配值超过阈值，则认为找到了匹配
    if best_match_val >= threshold:
        # 计算缩放后模板的尺寸
        scaled_template_h = int(template_gray.shape[0] * best_scale)
        scaled_template_w = int(template_gray.shape[1] * best_scale)

        # 计算匹配区域的中心点
        center_x = best_match_loc[0] + scaled_template_w // 2
        center_y = best_match_loc[1] + scaled_template_h // 2

        print(
            f"找到匹配! 位置: ({center_x}, {center_y}), 匹配度: {best_match_val:.4f}, 缩放比例: {best_scale:.2f}"
        )
        return (center_x, center_y)
    else:
        print(f"未找到匹配。最佳匹配度: {best_match_val:.4f}, 阈值: {threshold}")
        return None


def find_all_matches(
    template_path,
    threshold=0.8,
    scale_range=(0.5, 1.5),
    scale_step=0.05,
    max_results=10,
):
    """
    在屏幕截图中查找所有匹配模板图像的位置，支持不同缩放比例

    参数:
        template_path: 要查找的模板图像路径
        threshold: 匹配阈值，0-1之间，值越高要求匹配度越高
        scale_range: 缩放范围的元组 (最小缩放, 最大缩放)
        scale_step: 缩放步长
        max_results: 最大返回结果数

    返回:
        匹配位置的中心点坐标列表 [(x1, y1), (x2, y2), ...]
    """
    # 读取模板图像
    template = cv2.imread(str(template_path))
    if template is None:
        print(f"错误：无法读取模板图像 {template_path}")
        return []

    # 将模板转换为灰度图
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # 获取屏幕截图
    screenshot = pyautogui.screenshot()
    # 将PIL图像转换为OpenCV格式
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    # 转换为灰度图
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    all_matches = []
    best_scale = 1.0
    best_result = None

    # 尝试不同的缩放比例，找出最佳缩放比例
    current_scale = scale_range[0]
    while current_scale <= scale_range[1]:
        # 缩放模板
        scaled_template = cv2.resize(
            template_gray,
            None,
            fx=current_scale,
            fy=current_scale,
            interpolation=cv2.INTER_AREA if current_scale < 1 else cv2.INTER_LINEAR,
        )

        # 执行模板匹配
        result = cv2.matchTemplate(
            screenshot_gray, scaled_template, cv2.TM_CCOEFF_NORMED
        )

        # 查找最大值
        _, max_val, _, _ = cv2.minMaxLoc(result)

        # 如果这个缩放比例下有更好的匹配
        if max_val >= threshold and (
            best_result is None or max_val > np.max(best_result)
        ):
            best_result = result
            best_scale = current_scale

        current_scale += scale_step

    # 如果找不到任何匹配
    if best_result is None:
        print("未找到任何匹配")
        return []

    # 计算缩放后模板的尺寸
    scaled_template_h = int(template_gray.shape[0] * best_scale)
    scaled_template_w = int(template_gray.shape[1] * best_scale)

    # 在最佳缩放比例下找出所有匹配位置
    match_indices = np.where(best_result >= threshold)

    # 将匹配位置转换为列表
    match_positions = list(zip(match_indices[1], match_indices[0]))

    # 过滤重叠匹配 (使用非极大值抑制)
    filtered_matches = []
    match_positions.sort(key=lambda pos: best_result[pos[1], pos[0]], reverse=True)

    for match_pos in match_positions:
        # 检查是否与已有匹配重叠
        overlap = False
        for existing_match in filtered_matches:
            # 计算两个匹配框中心点之间的距离
            dist = np.sqrt(
                (match_pos[0] - existing_match[0]) ** 2
                + (match_pos[1] - existing_match[1]) ** 2
            )
            # 如果距离小于模板尺寸的一半，则视为重叠
            if dist < (scaled_template_w + scaled_template_h) / 4:
                overlap = True
                break

        if not overlap:
            filtered_matches.append(match_pos)
            # 限制最大结果数
            if len(filtered_matches) >= max_results:
                break

    # 计算中心点坐标
    center_points = []
    for match_pos in filtered_matches:
        center_x = match_pos[0] + scaled_template_w // 2
        center_y = match_pos[1] + scaled_template_h // 2
        match_val = best_result[match_pos[1], match_pos[0]]
        center_points.append((center_x, center_y))
        print(
            f"找到匹配! 位置: ({center_x}, {center_y}), 匹配度: {match_val:.4f}, 缩放比例: {best_scale:.2f}"
        )

    return center_points


def save_debug_image(template_path, matches=None, output_path="./tmp_img_save_folder/debug_match.png"):
    """
    保存带有匹配结果标记的截图，用于调试

    参数:
        template_path: 模板图像路径
        matches: 匹配位置列表 [(x1, y1), ...]，如果为None则重新进行匹配
        output_path: 输出图像路径
    """
    # 如果未提供匹配结果，则重新进行匹配
    if matches is None:
        matches = find_all_matches(template_path)
        if not matches:
            print("未找到匹配，无法生成调试图像")
            return

    # 读取模板图像获取尺寸
    template = cv2.imread(str(template_path))
    if template is None:
        print(f"错误：无法读取模板图像 {template_path}")
        return

    template_h, template_w = template.shape[:2]

    # 获取屏幕截图
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    # 在截图上标记匹配位置
    for center_x, center_y in matches:
        # 计算矩形左上角
        left = center_x - template_w // 2
        top = center_y - template_h // 2

        # 绘制矩形和中心点
        cv2.rectangle(
            screenshot,
            (left, top),
            (left + template_w, top + template_h),
            (0, 255, 0),
            2,
        )
        cv2.circle(screenshot, (center_x, center_y), 5, (0, 0, 255), -1)
        cv2.putText(
            screenshot,
            f"({center_x}, {center_y})",
            (center_x + 10, center_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2,
        )

    # 保存调试图像
    cv2.imwrite(output_path, screenshot)
    print(f"调试图像已保存至 {output_path}")


def main():
    parser = argparse.ArgumentParser(description="在屏幕中查找指定图像")
    parser.add_argument("template", help="要查找的模板图像路径")
    parser.add_argument(
        "--threshold", "-t", type=float, default=0.8, help="匹配阈值 (0-1)"
    )
    parser.add_argument("--min-scale", type=float, default=0.5, help="最小缩放比例")
    parser.add_argument("--max-scale", type=float, default=1.5, help="最大缩放比例")
    parser.add_argument("--scale-step", type=float, default=0.05, help="缩放步长")
    parser.add_argument("--all", "-a", action="store_true", help="查找所有匹配")
    parser.add_argument("--max-results", type=int, default=10, help="最大结果数量")
    parser.add_argument("--debug", "-d", action="store_true", help="保存调试图像")
    parser.add_argument(
        "--output", "-o", default="debug_match.png", help="调试图像输出路径"
    )

    args = parser.parse_args()

    # 确保模板图像存在
    template_path = Path(args.template)
    if not template_path.exists():
        print(f"错误：找不到模板图像 {template_path}")
        return 1

    # 根据参数选择查找单个匹配或所有匹配
    if args.all:
        matches = find_all_matches(
            template_path,
            threshold=args.threshold,
            scale_range=(args.min_scale, args.max_scale),
            scale_step=args.scale_step,
            max_results=args.max_results,
        )
    else:
        match = find_image_in_screenshot(
            template_path,
            threshold=args.threshold,
            scale_range=(args.min_scale, args.max_scale),
            scale_step=args.scale_step,
        )
        matches = [match] if match else []

    # 如果启用调试模式，保存调试图像
    if args.debug and matches:
        save_debug_image(template_path, matches, args.output)

    return 0


def match_and_click(image_path, threshold=0.6, debug_path="./tmp_img_save_folder/debug_match.png"):
    """
    查找并点击指定图片的位置
    :param image_path: 图片路径
    :param threshold: 匹配阈值
    """
    position = match_image(image_path, threshold=threshold, debug_path=debug_path)
    if position:
        x, y = position
        pyautogui.click(x, y)  # 点击匹配位置
        print(f"找到匹配位置：({x}, {y})", image_path)
        return x, y
    else:
        print("未找到匹配位置", image_path)
        return -1, -1


if __name__ == "__main__":
    main()
