import os
import time
import subprocess
from pathlib import Path


class ADBController:
    """
    通过ADB控制Android设备的类，提供截屏、点击、拖拽和缩放功能
    专门针对远程端口连接方式(127.0.0.1:16384)设计
    """

    def __init__(self, device_id="127.0.0.1:16384", adb_path="adb"):
        """
        初始化ADB控制器

        参数:
            device_id: 设备连接地址，默认为"127.0.0.1:16384"用于远程端口连接
            adb_path: adb可执行文件路径，默认为"adb"（假设adb已在环境变量中）
        """
        self.device_id = device_id
        self.adb_path = adb_path
        self._check_connection()

    def _check_connection(self):
        """
        检查ADB远程连接状态

        返回:
            bool: 如果连接成功返回True，否则引发异常
        """
        try:
            # 连接到指定端口
            subprocess.run(
                [self.adb_path, "connect", self.device_id],
                check=True,
                capture_output=True,
            )

            # 检查设备列表
            devices = self._execute_command("devices")
            connected_devices = [
                line for line in devices.strip().split("\n")[1:] if line.strip()
            ]

            if not connected_devices:
                raise ConnectionError("没有检测到ADB设备连接")

            print(f"ADB远程连接成功: {connected_devices}")
            return True

        except Exception as e:
            raise ConnectionError(f"ADB远程连接错误: {str(e)}")

    def _execute_command(self, command):
        """
        执行ADB命令

        参数:
            command: 要执行的ADB命令（不包含adb前缀）

        返回:
            str: 命令执行结果
        """
        cmd = [self.adb_path]
        if self.device_id:
            cmd.extend(["-s", self.device_id])

        cmd.extend(command.split())

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            # print(f"\t执行ADB命令: {' '.join(cmd)}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"ADB命令执行错误: {e}")
            print(f"错误输出: {e.stderr}")
            raise

    def screenshot(self, output_path="screen.png"):
        """
        截取手机屏幕并保存到本地

        参数:
            output_path: 输出图片路径，默认为当前目录下的screen.png

        返回:
            str: 保存的图片路径
        """
        # 确保输出目录存在
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # 临时文件路径（设备上）
        remote_file = "/sdcard/temp_screenshot.png"

        try:
            # 截图并保存到设备
            self._execute_command(f"shell screencap -p {remote_file}")

            # 将截图从设备拉取到本地
            self._execute_command(f"pull {remote_file} {output_path}")

            # 删除设备上的临时文件
            self._execute_command(f"shell rm {remote_file}")

            print(f"截图已保存至: {output_path}")
            return output_path
        except Exception as e:
            print(f"截图失败: {str(e)}")
            raise

    def tap(self, x, y):
        """
        模拟点击指定位置

        参数:
            x: 横坐标
            y: 纵坐标

        返回:
            bool: 操作是否成功
        """
        try:
            self._execute_command(f"shell input tap {x} {y}")
            print(f"点击位置: ({x}, {y})")
            return True
        except Exception as e:
            print(f"点击失败: {str(e)}")
            return False

    def swipe(self, start_x, start_y, end_x, end_y, duration=300, steps=10):
        """
        模拟从一个位置滑动到另一个位置

        参数:
            start_x: 起始点横坐标
            start_y: 起始点纵坐标
            end_x: 结束点横坐标
            end_y: 结束点纵坐标
            duration: 滑动持续时间(毫秒)，默认300ms
            steps: 滑动步数，越大越平滑，默认10

        返回:
            bool: 操作是否成功
        """
        try:

            self._execute_command(
                f"shell input swipe {start_x} {start_y} {end_x} {end_y} {duration}"
            )

            print(
                f"滑动: ({start_x}, {start_y}) -> ({end_x}, {end_y}), 持续时间: {duration}ms"
            )
            return True
        except Exception as e:
            print(f"滑动失败: {str(e)}")
            return False

    def swipe_relative(self, x, y, dx, dy, duration=300):
        """
        模拟从指定位置拖拽相对距离

        参数:
            x: 起始点横坐标
            y: 起始点纵坐标
            dx: 横向拖拽距离(正值向右，负值向左)
            dy: 纵向拖拽距离(正值向下，负值向上)
            duration: 拖拽持续时间(毫秒)，默认300ms

        返回:
            bool: 操作是否成功
        """
        return self.swipe(x, y, x + dx, y + dy, duration)

    def pinch_zoom(
        self, center_x, center_y, start_distance, end_distance, duration=300
    ):
        """
        模拟缩放手势

        参数:
            center_x: 缩放中心点横坐标
            center_y: 缩放中心点纵坐标
            start_distance: 起始两指间距离(像素)
            end_distance: 结束两指间距离(像素)
            duration: 手势持续时间(毫秒)，默认300ms

        返回:
            bool: 操作是否成功
        """
        try:
            # 计算两指的起始和结束位置
            half_start = start_distance / 2
            half_end = end_distance / 2

            # 第一个手指在水平方向移动(左侧)
            finger1_start_x = int(center_x - half_start)
            finger1_start_y = int(center_y)  # 保持y坐标不变，只在水平方向移动
            finger1_end_x = int(center_x - half_end)
            finger1_end_y = int(center_y)  # 保持y坐标不变

            # 第二个手指在水平方向移动(右侧)
            finger2_start_x = int(center_x + half_start)
            finger2_start_y = int(center_y)  # 保持y坐标不变，只在水平方向移动
            finger2_end_x = int(center_x + half_end)
            finger2_end_y = int(center_y)  # 保持y坐标不变

            # 标准的ADB不支持单命令多点触控，使用两个分开的swipe命令
            # 先执行一个手指的滑动
            self._execute_command(
                f"shell input swipe {finger1_start_x} {finger1_start_y} {finger1_end_x} {finger1_end_y} {duration}"
            )
            # 立即执行第二个手指的滑动
            self._execute_command(
                f"shell input swipe {finger2_start_x} {finger2_start_y} {finger2_end_x} {finger2_end_y} {duration}"
            )

            action = "放大" if end_distance > start_distance else "缩小"
            print(
                f"{action}手势: 从距离{start_distance}像素到{end_distance}像素, 中心点: ({center_x}, {center_y})"
            )
            return True
        except Exception as e:
            print(f"缩放操作失败: {str(e)}")
            return False

    def zoom_in(self, center_x, center_y, scale=1.5, duration=300):
        """
        模拟放大手势

        参数:
            center_x: 缩放中心点横坐标
            center_y: 缩放中心点纵坐标
            scale: 放大倍数，默认1.5倍
            duration: 手势持续时间(毫秒)，默认300ms

        返回:
            bool: 操作是否成功
        """
        base_distance = 100  # 基础距离(像素)
        return self.pinch_zoom(
            center_x, center_y, base_distance, base_distance * scale, duration
        )

    def zoom_out(self, center_x, center_y, scale=2, duration=500, steps=10):
        """
        使用高级触摸屏命令模拟双指缩小手势

        参数:
            center_x: 缩放中心点横坐标
            center_y: 缩放中心点纵坐标
            scale: 缩小倍数，默认2(缩小至原来的1/2)，值越大缩小效果越明显
            duration: 手势持续时间(毫秒)，默认500ms
            steps: 动画步数，越大越平滑，默认10

        返回:
            bool: 操作是否成功
        """
        try:
            # 转换duration为秒
            duration_sec = duration / 1000

            # 起始距离
            distance = 300  # 初始手指间距

            # 计算起始和结束坐标
            x1_start = center_x - distance
            x2_start = center_x + distance
            y1_start = y2_start = center_y

            # 根据缩放比例计算结束距离
            end_distance = int(distance / scale)
            x1_end = center_x - (end_distance // 2)
            x2_end = center_x + (end_distance // 2)
            y1_end = y2_end = center_y

            print(f"执行缩小: 从{distance}到{end_distance}, 缩小{scale}倍")

            # 计算每步延迟
            delay = duration_sec / steps

            # 按下两个手指
            self._execute_command(
                f"shell input touchscreen down {x1_start} {y1_start} 1"
            )
            self._execute_command(
                f"shell input touchscreen down {x2_start} {y2_start} 2"
            )
            self._execute_command("shell input touchscreen commit")

            # 模拟移动（缩小）
            for i in range(1, steps + 1):
                progress = i / steps
                nx1 = int(x1_start + (x1_end - x1_start) * progress)
                ny1 = int(y1_start + (y1_end - y1_start) * progress)
                nx2 = int(x2_start + (x2_end - x2_start) * progress)
                ny2 = int(y2_start + (y2_end - y2_start) * progress)

                self._execute_command(f"shell input touchscreen move {nx1} {ny1} 1")
                self._execute_command(f"shell input touchscreen move {nx2} {ny2} 2")
                self._execute_command("shell input touchscreen commit")
                time.sleep(delay)

            # 释放两个手指
            self._execute_command(f"shell input touchscreen up {x1_end} {y1_end} 1")
            self._execute_command(f"shell input touchscreen up {x2_end} {y2_end} 2")
            self._execute_command("shell input touchscreen commit")

            print(
                f"缩小手势完成: 从距离{distance}像素到{end_distance}像素, 中心点: ({center_x}, {center_y})"
            )
            return True

        except Exception as e:
            print(f"高级触摸缩小操作失败: {str(e)}")
            return False

    def get_screen_size(self):
        """
        获取屏幕尺寸

        返回:
            tuple: (宽度, 高度) 屏幕尺寸
        """
        try:
            output = self._execute_command("shell wm size")
            # 输出格式如: Physical size: 1080x2340
            if "Physical size:" in output:
                size_part = output.split("Physical size:")[1].strip()
                width, height = map(int, size_part.split("x"))
                return width, height
            else:
                raise ValueError("无法解析屏幕尺寸")
        except Exception as e:
            print(f"获取屏幕尺寸失败: {str(e)}")
            raise

    def input_text(self, text):
        """
        输入文本

        参数:
            text: 要输入的文本

        返回:
            bool: 操作是否成功
        """
        try:
            # 转义特殊字符
            escaped_text = text.replace(" ", "%s").replace("'", "'").replace('"', '"')
            self._execute_command(f'shell input text "{escaped_text}"')
            print(f"输入文本: {text}")
            return True
        except Exception as e:
            print(f"文本输入失败: {str(e)}")
            return False


# 使用示例
if __name__ == "__main__":
    try:
        # 初始化ADB控制器（默认使用系统中的adb命令连接到127.0.0.1:16384）
        adb = ADBController()

        # 获取屏幕尺寸
        width, height = adb.get_screen_size()
        print(f"屏幕尺寸: {width}x{height}")

        # 截图
        screenshot_path = adb.screenshot("current_screen.png")

        # 点击屏幕中心
        center_x, center_y = width // 2, height // 2
        adb.tap(center_x, center_y)

        # 向上滑动
        adb.swipe_relative(center_x, center_y, 0, -300)

        # 演示放大和缩小操作
        adb.zoom_in(center_x, center_y)
        time.sleep(1)
        adb.zoom_out(center_x, center_y)

    except Exception as e:
        print(f"演示过程中出错: {str(e)}")
