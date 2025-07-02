from adb_controller import ADBController
from template_matcher import TemplateMatcher
import time

# 创建实例
adb = ADBController()  # 使用我们之前创建的ADB控制器
matcher = TemplateMatcher(adb)


def click_img_postion(img_path, threshold=0.8):
    """
    查找并点击指定图片位置
    :param img_path: 图片路径
    :param threshold: 匹配阈值
    """
    result = matcher.find_and_tap(img_path, threshold)
    if result:
        print(f"点击成功，图片 {img_path} 已点击")
        time.sleep(2)  # 等待1秒，确保点击生效
        return True
    else:
        print("未找到匹配的图片", img_path)
        return False


# click_img_postion("./night_world/jingong.png", threshold=0.8)
# click_img_postion("./night_world/li-ji-xun-zhao.png", threshold=0.8)
# time.sleep(5)  # 等待2秒，确保操作生效
# # 找到该图片的坐标并打印
# result = matcher.find_template(
#     "./night_world/ying-xiong.png", threshold=0.8, debug_image="jingong_debug.png"
# )
# if result:
#     center_x, center_y, _ = result
#     adb.tap(center_x, center_y)
#     put_position_x = center_x
#     put_position_y = center_y - 260
#     adb.tap(put_position_x, put_position_y)  # 再次点击以确保操作生效

#     new_x = center_x
#     for item in range(0, 6):
#         new_x += 120
#         adb.tap(new_x, center_y)
#         adb.tap(put_position_x, put_position_y)
#         adb.tap(new_x, center_y)

# start_time = time.time()

# while time.time() - start_time < 120:
#     r = click_img_postion("./night_world/hui_ying.png", threshold=0.8)
#     if r:
#         break
#     else:
#         # 激活英雄技能
#         adb.tap(center_x, center_y)
#         time.sleep(5)


# x, y = adb.get_screen_size()

# adb.swipe(500, 500, 500, 900, duration=200)  # 向上滑动
# time.sleep(2)  # 等待2秒，确保滑动生效
# click_img_postion("./adb_spec/adb_shuiche.png", threshold=0.8)
# click_img_postion("./night_world/shou-ji.png", threshold=0.8)
# click_img_postion("./night_world/x.png", threshold=0.8)


def attack_night_village(iterations=1):
    """
    执行夜世界的进攻操作

    参数:
        iterations: 执行次数，默认为1次

    返回:
        bool: 操作是否成功
    """
    try:
        # 初始化ADB控制器和图像匹配器
        adb = ADBController()
        matcher = TemplateMatcher(adb)

        # 定义点击图像位置的函数
        def click_img_postion(image_path, threshold=0.8, max_retries=3):
            for _ in range(max_retries):
                result = matcher.find_template(image_path, threshold=threshold)
                if result:
                    center_x, center_y, _ = result
                    adb.tap(center_x, center_y)
                    print(f"点击图像 {image_path} 成功")
                    return True
                time.sleep(1)
            print(f"未找到图像 {image_path}")
            return False

        # 执行指定次数的攻击
        for iteration in range(iterations):
            print(f"开始第 {iteration + 1}/{iterations} 次夜世界进攻")

            # 点击进攻按钮
            click_img_postion("./night_world/jingong.png", threshold=0.8)
            click_img_postion("./night_world/li-ji-xun-zhao.png", threshold=0.8)
            time.sleep(5)  # 等待5秒，确保操作生效

            # 找到英雄图片的坐标并部署
            result = matcher.find_template(
                "./night_world/ying-xiong.png",
                threshold=0.8,
                debug_image="jingong_debug.png",
            )
            if result:
                center_x, center_y, _ = result
                adb.tap(center_x, center_y)
                put_position_x = center_x
                put_position_y = center_y - 260
                adb.tap(put_position_x, put_position_y)  # 再次点击以确保操作生效

                # 部署更多英雄
                new_x = center_x
                for item in range(0, 6):
                    new_x += 120
                    adb.tap(new_x, center_y)
                    adb.tap(put_position_x, put_position_y)
                    adb.tap(new_x, center_y)

                # 等待战斗结束或激活英雄技能
                start_time = time.time()
                waite_time = 120
                while time.time() - start_time < waite_time:  # 最长等待2分钟
                    r = click_img_postion("./night_world/hui_ying.png", threshold=0.8)
                    if r:
                        break
                    else:
                        # 激活英雄技能
                        adb.tap(center_x, center_y)

                    r = click_img_postion("./night_world/2.png", threshold=0.8)
                    # 打赢了，继续打第二场
                    waite_time = waite_time + 120
                    if r:
                        new_x = center_x
                        for item in range(0, 8):
                            adb.tap(new_x, center_y)
                            adb.tap(put_position_x, put_position_y)
                            adb.tap(new_x, center_y)
                            new_x += 120
                    time.sleep(5)

                # 获取屏幕大小
                x, y = adb.get_screen_size()
                time.sleep(2)  # 等待2秒，确保操作生效
                # 向下滑动查找水车
                adb.swipe(500, 500, 500, 900, duration=200)  # 向下滑动
                time.sleep(2)  # 等待2秒，确保滑动生效

                # 点击水车、收集和关闭按钮
                if click_img_postion("./adb_spec/adb_shuiche.png", threshold=0.6):
                    click_img_postion("./night_world/shou-ji.png", threshold=0.8)
                    click_img_postion("./night_world/x.png", threshold=0.8)

                # 每次攻击完成后等待5秒
                time.sleep(5)

            else:
                print("未找到英雄图标，跳过本次攻击")

        print(f"完成了 {iterations} 次夜世界进攻")
        return True

    except Exception as e:
        print(f"夜世界进攻过程中出错: {str(e)}")
        return False


if __name__ == "__main__":
    attack_night_village(iterations=3)
