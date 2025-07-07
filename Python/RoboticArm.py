import socket
import requests
import threading
import time
import logging
from datetime import datetime

# 硬编码两个机械臂的IP地址
ARM1_IP = "192.168.43.6"  # 第一个机械臂的IP
ARM2_IP = "192.168.43.111"  # 第二个机械臂的IP

# 配置日志记录器
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 输出到控制台
        logging.FileHandler('arm_debug.log')  # 输出到文件
    ]
)
logger = logging.getLogger(__name__)

# 全局变量用于存储调试信息
last_debug_output = time.time()
debug_info = {
    "last_position": "",
    "last_commands": [],
    "start_time": datetime.now()
}


def send_command(ip, command):
    """向指定IP的机械臂发送单个命令"""
    try:
        url = f"http://{ip}/js?json={command}"
        response = requests.get(url, timeout=3)
        return response.text
    except requests.RequestException:
        return None


def send_to_robot_arms(position):
    """接收坐标并直接发送到两个机械臂"""
    try:
        # 直接存储原始坐标用于调试
        debug_info["last_position"] = position

        # 分割坐标字符串为6个数值
        coordinates = [float(coord) for coord in position.split(',')]
        if len(coordinates) != 6:
            return

        # 直接解析为两个机械臂的坐标
        arm1_coords = coordinates[0:3]  # x1, y1, z1
        arm2_coords = coordinates[3:6]  # x2, y2, z2
        arm1_coords[2] += 150
        arm2_coords[2] += 150
        # 坐标限幅处理（保持安全范围）

        def clamp(x, min_val, max_val):
            return max(min(x, max_val), min_val)

        # 对每个坐标值进行限幅
        clamped_arm1 = [clamp(coord, -400, 400) for coord in arm1_coords]
        clamped_arm2 = [clamp(coord, -400, 400) for coord in arm2_coords]

        # 构造命令 (使用固定t=3.14，但使用实际坐标值)
        arm1_command = f'{{"T":1041,"x":200,"y":{clamped_arm1[1]:.1f},"z":{clamped_arm1[2]:.1f},"t":3.14}}'
        arm2_command = f'{{"T":1041,"x":200,"y":{clamped_arm2[1]:.1f},"z":{clamped_arm2[2]:.1f},"t":3.14}}'

        # 存储命令用于调试
        debug_info["last_commands"] = [arm1_command, arm2_command]

        # 直接发送命令给相应的机械臂
        def send_to_arm(ip, cmd):
            send_command(ip, cmd)

        # 使用线程同时发送
        t1 = threading.Thread(target=send_to_arm, args=(ARM1_IP, arm1_command))
        t2 = threading.Thread(target=send_to_arm, args=(ARM2_IP, arm2_command))

        t1.start()
        t2.start()

        t1.join()
        t2.join()

    except (IndexError, ValueError):
        pass


def print_debug_info():
    """每秒输出一次调试信息"""
    global last_debug_output

    current_time = time.time()
    if current_time - last_debug_output >= 1.0:
        # 准备调试信息
        debug_output = [
            f"\n=== 系统状态 [{datetime.now().strftime('%H:%M:%S')}] ==="
        ]

        # 解析原始坐标
        if debug_info["last_position"]:
            raw_coords = debug_info["last_position"].split(',')
            if len(raw_coords) >= 6:
                point1 = f"({raw_coords[0]}, {raw_coords[1]}, {raw_coords[2]})"
                point2 = f"({raw_coords[3]}, {raw_coords[4]}, {raw_coords[5]})"
                debug_output.append(f"原始坐标: ARM1: {point1}  ARM2: {point2}")

        # 添加发送的指令
        if debug_info["last_commands"]:
            debug_output.append("发送给机械臂的指令:")
            for i, cmd in enumerate(debug_info["last_commands"]):
                debug_output.append(f"  机械臂{i + 1}: {cmd}")

        debug_output.append("=" * 40)

        # 输出到控制台
        logger.info("\n".join(debug_output))

        last_debug_output = current_time


def main():
    host = '127.0.0.1'
    port = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    logger.info("Waiting for Unity to connect...")
    logger.info(f"Arm1 IP: {ARM1_IP}, Arm2 IP: {ARM2_IP}")

    client_socket, client_address = server_socket.accept()
    logger.info(f"Connected by {client_address}")

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            position = data.decode('utf-8').strip()
            logger.info(f"Received position: {position}")
            send_to_robot_arms(position)
            print_debug_info()  # 每次处理完数据后检查是否需要输出调试信息
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
    finally:
        client_socket.close()
        server_socket.close()
        logger.info("Connection closed")


if __name__ == "__main__":
    main()
