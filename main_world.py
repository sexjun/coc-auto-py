from image_matcher import match_and_click, match_image
import pyautogui
import time
import random


def fang_bing(x, y, count):
    """
    放兵函数
    """
    if x == -1 or y == -1:
        print("未找到放兵位置")
        return
    # 使用match_and_click函数匹配并点击放兵位置，设置阈值为0.3
    pyautogui.PAUSE = 0.01
    for item in range(1, count + 1):
        pyautogui.click(x, y)
        print("clicked at:", x, y, "item:", item)


# def zhuye_status_check():
#     match_and_click(
#         "./zhushijie/zhu-ye.png", threshold=0.8, debug_path="zhuye_debug.png"
#     )


def auto_attack_battle_advanced(
    times=1, troop_count=20, battle_timeout=120, round_delay=5, check_interval=3
):
    """
    高级自动攻击战斗函数

    Args:
        times (int): 执行次数，默认为1次
        troop_count (int): 放兵数量，默认20个
        battle_timeout (int): 战斗超时时间（秒），默认120秒
        round_delay (int): 轮次间延迟时间（秒），默认5秒
        check_interval (int): 检查回营按钮的间隔时间（秒），默认3秒
    """
    for battle_round in range(1, times + 1):
        print(f"\n=== 开始第 {battle_round}/{times} 轮攻击 ===")

        try:
            pyautogui.PAUSE = 0.01

            # 攻击流程
            print(f"第 {battle_round} 轮：开始攻击流程...")
            match_and_click("./zhushijie/jin-gong.png", threshold=0.5)
            time.sleep(1)
            match_and_click("./zhushijie/sou-su.png", threshold=0.5)
            time.sleep(1)
            pyautogui.FAILSAFE = False  # 禁用鼠标移动到屏幕角落时的安全机制

            # 选择放兵的位置
            fangbing_weizhi = [
                "./zhushijie/fang-bing.png",
                "./zhushijie/fang-bing2.png",
                "./zhushijie/fang-bing3.png",
                "./zhushijie/fang-bing4.png",
                "./zhushijie/fang-bing5.png",
                "./zhushijie/fang-bing6.png",
                "./zhushijie/fang-bing7.png",
            ]
            random.shuffle(fangbing_weizhi)
            print(fangbing_weizhi)  # 输出打乱后的列表
            for location in fangbing_weizhi:
                fang_bing_x, fang_bing_y = match_and_click(
                    location, threshold=0.8, debug_path="fangbing_debug.png"
                )
                if fang_bing_x != -1 and fang_bing_y != -1:
                    print(
                        f"第 {battle_round} 轮：找到放兵位置 {location}，x: {fang_bing_x}, y: {fang_bing_y}"
                    )
                    break

            if fang_bing_x == -1 or fang_bing_y == -1:
                print("未找到放兵位置")
                continue

            # 放黄毛
            x, y = match_and_click("./zhushijie/huang-mao.png", threshold=0.8)
            time.sleep(1)
            pyautogui.click(x, y)
            fang_bing(fang_bing_x, fang_bing_y, troop_count)

            # 放部落兵
            # x, y = match_and_click("./zhushijie/cheng-bao.png")
            # time.sleep(1)
            # pyautogui.click(x, y)
            # fang_bing(fang_bing_x, fang_bing_y, 2)

            # 放哥布林
            x, y = match_and_click("./zhushijie/ge-bo-lin.png")
            time.sleep(1)
            pyautogui.click(x, y)
            fang_bing(fang_bing_x, fang_bing_y, 40)

            # 放弓箭手
            # x, y = match_and_click("./zhushijie/gong-jian-shou.png")
            # time.sleep(1)
            # pyautogui.click(x, y)
            # fang_bing(fang_bing_x, fang_bing_y, 10)

            # 等待战斗结束
            print(f"第 {battle_round} 轮：等待战斗结束（最长{battle_timeout}秒）...")
            start_time = time.time()
            check_count = 0

            while time.time() - start_time < battle_timeout:
                elapsed_time = time.time() - start_time
                check_count += 1

                x, y = match_and_click("./zhushijie/hui-ying.png", threshold=0.9)
                if x != -1 and y != -1:
                    print(f"第 {battle_round} 轮：战斗结束！用时: {elapsed_time:.1f}秒")
                    break
                else:
                    print(
                        f"第 {battle_round} 轮：第 {check_count} 次检查 - 用时: {elapsed_time:.1f}秒"
                    )
                    time.sleep(check_interval)

            if time.time() - start_time >= battle_timeout:
                print(f"第 {battle_round} 轮：战斗超时")

            # 轮次间延迟
            if battle_round < times:
                print(f"等待{round_delay}秒后开始下一轮...")
                time.sleep(round_delay)

        except Exception as e:
            print(f"第 {battle_round} 轮执行出错: {str(e)}")
            continue

    print(f"\n=== 攻击任务完成！总共 {times} 轮 ===")


# 使用示例
if __name__ == "__main__":
    pyautogui.FAILSAFE = False  # 禁用鼠标移动到屏幕角落时的安全机制

    # 高级配置使用
    auto_attack_battle_advanced(
        times=15, troop_count=60, battle_timeout=260, round_delay=3
    )
