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
    "last_transformed_position": "",  # 存储变换后的坐标
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
    """处理坐标并发送到两个机械臂"""
    try:
        coordinates = position.split(',')
        if len(coordinates) != 6:
            return

        # 存储原始坐标用于调试
        debug_info["last_position"] = position

        # === 坐标变换处理 ===
        transformed_coords = []
        # 对每个物体的三个坐标分别处理
        for i in range(0, len(coordinates), 3):
            try:
                if i == 0:  # 第一个物体对应ARM1
                    x = (-float(coordinates[i]) - 47) * 300
                    y = 200
                    z = 200
                    y += 150
                    x -= 160
                if i == 3:  # 第二个物体对应ARM2
                    x = (-float(coordinates[i]) - 45.6) * 300
                    y = 200
                    z = 200
                    y += 150

                transformed_coords.extend(
                    [round(x, 1), round(y, 1), round(z, 1)])
            except (IndexError, ValueError):
                transformed_coords.extend([0.0, 0.0, 0.0])

        # 存储变换后的坐标用于调试
        transformed_str = ",".join([f"{x:.1f}" for x in transformed_coords])
        debug_info["last_transformed_position"] = transformed_str
        # === 坐标变换结束 ===

        # 解析两个物体的坐标（使用变换后的坐标）
        coords = [
            (transformed_coords[0], transformed_coords[1],
             transformed_coords[2]),
            (transformed_coords[3],
             transformed_coords[4], transformed_coords[5])
        ]

        # 坐标限幅处理
        def clamp(x, min_val, max_val):
            return max(min(x, max_val), min_val)

        clamped_coords = []
        for x, y, z in coords:
            clamped_coords.append((
                clamp(x, -400, 400),
                clamp(y, 0, 400),
                z  # z值不参与机械臂控制，但保留处理
            ))

        # 构造命令 (使用固定x=150和t=3.14)
        commands = []
        for y, z, _ in clamped_coords:  # 使用y和z，忽略原始z值
            command = f'{{"T":1041,"x":200,"y":{y},"z":200,"t":3.14}}'
            commands.append(command)

        # 存储命令用于调试
        debug_info["last_commands"] = commands

        # 分配命令给机械臂（第一个给机械臂1，第二个给机械臂2）
        arm1_commands = [commands[0]]
        arm2_commands = [commands[1]]

        # 创建发送线程
        def send_to_arm(ip, cmds):
            for cmd in cmds:
                send_command(ip, cmd)

        t1 = threading.Thread(target=send_to_arm,
                              args=(ARM1_IP, arm1_commands))
        t2 = threading.Thread(target=send_to_arm,
                              args=(ARM2_IP, arm2_commands))

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
                debug_output.append(f"原始坐标: 第一个点: {point1} 第二个点: {point2}")

        # 解析变换后的坐标
        if debug_info["last_transformed_position"]:
            trans_coords = debug_info["last_transformed_position"].split(',')
            if len(trans_coords) >= 6:
                point1 = f"({trans_coords[0]}, {trans_coords[1]}, {trans_coords[2]})"
                point2 = f"({trans_coords[3]}, {trans_coords[4]}, {trans_coords[5]})"
                debug_output.append(f"转换后坐标: 第一个点: {point1} 第二个点: {point2}")

        # 添加发送的指令
        if debug_info["last_commands"]:
            debug_output.append("发送给机械臂的指令:")
            for i, cmd in enumerate(debug_info["last_commands"]):
                debug_output.append(f"  机械臂{i+1}: {cmd}")

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
            logger.info(data)
            if not data:
                break
            position = data.decode('utf-8').strip()
            send_to_robot_arms(position)
            print_debug_info()  # 每次处理完数据后检查是否需要输出调试信息
    except Exception:
        pass
    finally:
        client_socket.close()
        server_socket.close()
        logger.info("Connection closed")


if __name__ == "__main__":
    main()
