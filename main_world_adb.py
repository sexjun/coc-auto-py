from image_matcher import match_and_click, match_image
from adb_controller import ADBController
from template_matcher import TemplateMatcher
import time
import random

# 创建实例
adb = ADBController()  # 使用我们之前创建的ADB控制器
matcher = TemplateMatcher(adb)


def fang_bing(x, y, count):
    """
    放兵函数
    """
    if x == -1 or y == -1:
        print("未找到放兵位置")
        return
    # 使用match_and_click函数匹配并点击放兵位置，设置阈值为0.3
    for item in range(1, count + 1):
        adb.tap(x, y)  # 使用ADB点击
        time.sleep(random.uniform(0.01, 0.05))  # 确保点击间隔


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


import time
import random


def auto_battle(call_count=1):
    """
    自动化战斗函数

    Args:
        call_count (int): 调用次数，默认为1次
    """

    for i in range(call_count):
        print(f"开始第 {i+1} 次战斗...")

        try:
            # 点击进攻按钮
            click_img_postion("./zhushijie/jin-gong.png", threshold=0.5)
            time.sleep(1)

            # 点击搜索按钮
            click_img_postion("./zhushijie/sou-su.png", threshold=0.5)
            time.sleep(1)

            # 寻找放兵位置
            fangbing_x, fangbing_y = find_fangbing_position()
            if fangbing_x == 0:
                print(f"第 {i+1} 次战斗：未找到放兵位置，跳过本次战斗")
                continue

            # 部署所有兵种
            deploy_all_armies(fangbing_x, fangbing_y)

            # 等待战斗结束
            battle_result = wait_for_battle_end()

            if battle_result:
                print(f"第 {i+1} 次战斗完成")
            else:
                print(f"第 {i+1} 次战斗超时")

        except Exception as e:
            print(f"第 {i+1} 次战斗出现错误: {e}")
            continue

        # 如果不是最后一次调用，添加间隔时间
        if i < call_count - 1:
            print("等待下一次战斗...")
            time.sleep(2)

    print(f"所有 {call_count} 次战斗已完成")


def find_fangbing_position():
    """
    寻找放兵位置

    Returns:
        tuple: (x坐标, y坐标)
    """
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

    for location in fangbing_weizhi:
        r = matcher.find_template(
            location,
            threshold=0.6,
            debug_image="./tmp_img_save_folder/fangbing_deubg.png",
        )
        if r:
            fangbing_x, fangbing_y, _ = r
            print(f"找到放兵位置 {location}，x: {fangbing_x}")
            return fangbing_x, fangbing_y

    print("未找到放兵位置")
    return 0, 0


def deploy_all_armies(fangbing_x, fangbing_y):
    """
    部署所有兵种

    Args:
        fangbing_x (int): 放兵位置x坐标
        fangbing_y (int): 放兵位置y坐标
    """
    all_arm_postions = []
    all_arm_postions.append(
        {"huang-mao": matcher.find_template("./zhushijie/huang-mao.png", threshold=0.8)}
    )
    all_arm_postions.append(
        {"ge-bu-lin": matcher.find_template("./zhushijie/ge-bo-lin.png", threshold=0.8)}
    )
    all_arm_postions.append(
        {
            "archer": matcher.find_template(
                "./zhushijie/gong-jian-shou.png", threshold=0.8
            )
        }
    )

    # 释放所有作战单位
    for arm in all_arm_postions:
        for key, value in arm.items():
            if value:
                x, y, _ = value
                print(f"找到兵种 {key}，x: {x}，y: {y}")
                time.sleep(0.3)
                adb.tap(x, y)
                time.sleep(0.2)
                fang_bing(fangbing_x, fangbing_y, 50)


def wait_for_battle_end(timeout=240):
    """
    等待战斗结束

    Args:
        timeout (int): 超时时间，默认240秒

    Returns:
        bool: True表示战斗正常结束，False表示超时
    """
    start_time = time.time()
    time.sleep(20)  # 等待20s开始检测， 这个时候战斗还在进行中。
    while time.time() - start_time < timeout:
        elapsed_time = time.time() - start_time

        if click_img_postion("./zhushijie/hui-ying.png", threshold=0.8):
            print("战斗结束")
            time.sleep(3)
            return True
        else:
            time.sleep(5)

    print("战斗超时")
    return False


# 使用示例：
if __name__ == "__main__":
    # 调用1次
    auto_battle(2)

    # 调用5次
    # auto_battle(5)

    # 调用10次
    # auto_battle(10)
