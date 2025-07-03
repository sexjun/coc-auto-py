from image_matcher import match_image, match_and_click
import pyautogui
import time


# """

# 自动游戏战斗函数
# 这里是根据当前屏幕截图进行匹配的，模拟器不能隐藏，已经废弃。改为使用adb控制器。
# 该文件备份，留着以后参考
# """

import time
import pyautogui


def found_shuizhe_view():
    x, y = match_and_click("./night_world/zhong-lou.png", threshold=0.5)
    if x == -1 or y == -1:
        print("未找到中楼按钮，无法执行操作")
        return
    pyautogui.click(x - 10, y - 20)  # 点击中楼按钮
    pyautogui.scroll(-500)
    pyautogui.scroll(-500)
    pyautogui.scroll(-500)
    pyautogui.scroll(-500)
    x, y = match_and_click("./night_world/base_.png", threshold=0.5)  # 查找圣水按钮
    time.sleep(1)  # 等待1秒
    pyautogui.dragRel(0, 100, duration=0.2)  # 拖动到圣水位置
    pyautogui.dragRel(0, 100, duration=0.2)  # 拖动到圣水位置


def collect_shengshui():
    x, y = match_and_click("./night_world/shui_che.png", threshold=0.6)  # 查找圣水按钮
    if x == -1 or y == -1:
        print("未找到圣水车，无法收集圣水")
        return
    x, y = match_and_click("./night_world/shou-ji.png", threshold=0.6)  # 查找圣水按钮
    time.sleep(1)  # 等待1秒
    x, y = match_and_click("./night_world/x.png", threshold=0.6)  # 查找圣水按钮


def auto_game_battle(times=1):
    """
    自动游戏战斗函数

    Args:
        times (int): 执行次数，默认为1次
    """
    for battle_round in range(1, times + 1):
        print(f"\n=== 开始第 {battle_round}/{times} 轮战斗 ===")

        try:
            # 初始化战斗
            match_and_click("./night_world/jingong.png")
            match_and_click(
                "./night_world/li-ji-xun-zhao.png", threshold=0.4
            )  # 调整阈值以提高匹配灵活度

            time.sleep(4)  # 等待4秒
            x, y = match_and_click(
                "./night_world/ying-xiong.png", threshold=0.8
            )  # 查找英雄位置

            yingyong_x = x
            yingyong_y = y

            if x == -1 or y == -1:
                print(f"第 {battle_round} 轮：未找到英雄匹配位置，跳过本轮")
                continue

            # 设置兵种位置
            fangbing_x = x
            fangbing_y = y - 250
            pyautogui.click(fangbing_x, fangbing_y)  # 点击匹配位置
            print(f"第 {battle_round} 轮：放英雄位置: {fangbing_x}, {fangbing_y}")

            pyautogui.PAUSE = 0.5  # 设置全局点击间隔
            pyautogui.FAILSAFE = True  # 启用鼠标移动到屏幕

            # 部署多个兵种
            new_x = x
            for i in range(4):
                new_x = new_x + 160
                pyautogui.click(new_x, y)  # 点击匹配位置
                pyautogui.click(fangbing_x, fangbing_y)  # 点击匹配位置
                pyautogui.click(new_x, y)  # 点击匹配位置

            # 战斗监控循环
            start_time = time.time()
            duration = 120  # 120秒
            interval = 5  # 5秒间隔
            count = 1

            print(f"第 {battle_round} 轮：开始战斗监控，最长120秒...")

            while time.time() - start_time < duration:
                current_time = time.strftime("%Y-%m-%d %H:%M:%S")
                elapsed = int(time.time() - start_time)
                print(
                    f"第 {battle_round} 轮 - 监控 {count} - 时间: {current_time} - 已运行: {elapsed}秒"
                )

                # 尝试释放技能
                pyautogui.click(yingyong_x, yingyong_y)

                # 检查是否出现回营按钮
                x_hui, y_hui = match_and_click(
                    "./night_world/hui_ying.png", threshold=0.9
                )
                if x_hui != -1 and y_hui != -1:
                    print(f"第 {battle_round} 轮：发现回营按钮，战斗结束")
                    break

                # 检查是否出现结束按钮
                x_end, y_end = match_and_click("./night_world/2.png", threshold=0.9)
                if x_end != -1 and y_end != -1:
                    print(f"第 {battle_round} 轮：发现结束按钮，执行结束流程")
                    # 放置英雄
                    pyautogui.click(yingyong_x, yingyong_y)  # 点击英雄位置结束按钮
                    pyautogui.click(fangbing_x, fangbing_y)  # 点击英雄位置结束按钮

                    # 放置兵种
                    new_x = fangbing_x
                    for i in range(5):
                        new_x = new_x + 160
                        pyautogui.click(new_x, y)  # 点击匹配位置
                        pyautogui.click(fangbing_x, fangbing_y)  # 点击匹配位置
                        pyautogui.click(new_x, y)  # 点击匹配位置
                        duration = 240

                    # match_and_click("./night_world/jieshu.png", threshold=0.9)  # 点击结束按钮
                    # match_and_click("./night_world/queren.png", threshold=0.9)  # 点击确认按钮
                    # match_and_click("./night_world/hui_ying.png", threshold=0.9)  # 再次查找回营按钮
                    # break

                count += 1
                time.sleep(interval)

            print(f"第 {battle_round} 轮战斗完成！ 手机资源收集中...")
            time.sleep(2)  # 等待2秒
            found_shuizhe_view()
            collect_shengshui()
            # 轮次间间隔
            if battle_round < times:
                print(f"等待3秒后开始第 {battle_round + 1} 轮...")
                time.sleep(3)

        except Exception as e:
            print(f"第 {battle_round} 轮执行出错: {str(e)}")
            continue

    print(f"\n=== 所有战斗完成！总共执行了 {times} 轮 ===")


# 使用示例
if __name__ == "__main__":
    # 执行1次
    # auto_game_battle(1)

    # 执行3次
    auto_game_battle(3)
    # found_shuizhe_view()

# # 查找所有匹配
# all_matches = match_image("按钮图片.png", find_all=True)
# for i, pos in enumerate(all_matches):
#     print(f"匹配 #{i+1}: 位置 = {pos}")

# # 保存调试图像
# match_image("按钮图片.png", save_debug=True, debug_path="结果图.png")

# # 调整匹配参数
# match_image(
#     "按钮图片.png",
#     threshold=0.7,  # 降低匹配阈值，增加匹配灵活度
#     scale_range=(0.8, 1.2),  # 限制缩放范围
#     scale_step=0.1,
# )  # 提高缩放步长以提升性能
