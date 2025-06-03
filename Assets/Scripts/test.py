import socket
import requests
import argparse

# 定义机械臂通信函数


def send_to_robot_arm(ip_addr, position):
    # 固定 t 值，这里假设 t 为 3.14
    t = 3.14
    try:
        # unity 0:x 1:y 2:z
        # robot arm x stable 0<y<400 0<z<400
        coordinates = position.split(',')
        x = 150
        unity_x, unity_y, unity_z = float(coordinates[0]), float(
            coordinates[1]), float(coordinates[2])
        if (unity_x < 0):
            unity_x = 0
        if (unity_x > 400):
            unity_x = 400
        if (unity_y < 0):
            unity_y = 0
        if (unity_y > 400):
            unity_y = 400
        y = unity_x
        z = unity_y

        # 构造JSON语句
        command = '{"T":1041,"x":%s,"y":%s,"z":%s,"t":%s}' % (
            x, y, z, t)
        # 构造请求URL
        url = "http://" + ip_addr + "/js?json=" + command
        response = requests.get(url)
        content = response.text
        print(content)
    except (IndexError):
        print("Received invalid index data from Unity.")
    except (ValueError):
        print("Received invalid coordinate data from Unity.")
    except requests.RequestException as e:
        print(f"Error sending request to the robot arm: {e}")


def main():
    # 创建命令行参数解析器，用于接收IP地址
    parser = argparse.ArgumentParser(description='Http JSON Communication')
    parser.add_argument('ip', type=str, help='IP address: 192.168.10.104')
    args = parser.parse_args()
    ip_addr = args.ip

    host = '127.0.0.1'
    port = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    print("Waiting for Unity to connect...")

    client_socket, client_address = server_socket.accept()
    print(f"Connected by {client_address}")

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            position = data.decode('utf-8').strip()
            print(f"Received position: {position}")
            # 将接收到的位置信息发送给机械臂
            send_to_robot_arm(ip_addr, position)
    finally:
        client_socket.close()
        server_socket.close()


if __name__ == "__main__":
    main()
