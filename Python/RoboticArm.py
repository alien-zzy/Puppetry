import socket
import requests
import threading
import time
import logging
from datetime import datetime

# Hardcoded IP addresses for three robotic arms
ARM1_IP = "192.168.43.6"  # First robotic arm IP
ARM2_IP = "192.168.43.111"  # Second robotic arm IP
ARM3_IP = "192.168.43.53"  # Third robotic arm IP

# Configure logger only for file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('arm_debug.log')  # Output to file only
    ]
)
logger = logging.getLogger(__name__)


def send_command(ip, command):
    """Send a single command to the robotic arm at the specified IP"""
    try:
        url = f"http://{ip}/js?json={command}"
        response = requests.get(url, timeout=3)
        return response.text
    except requests.RequestException:
        return None


def send_to_robot_arms(position):
    """Receive coordinates and send to three robotic arms"""
    try:
        # Print raw coordinates from Unity to terminal
        print(f"[RECEIVED] Raw coordinates from Unity: {position}")

        # Split coordinate string into 9 values (three points, each x,y,z)
        coordinates = [float(coord) for coord in position.split(',')]
        if len(coordinates) != 9:
            print(
                f"[ERROR] Invalid coordinate data: Expected 9 values, received {len(coordinates)}")
            logger.error(
                f"Invalid coordinate data: Expected 9 values, received {len(coordinates)}")
            return

        # Parse coordinates for each robotic arm
        arm1_coords = coordinates[0:3]  # x1, y1, z1
        arm2_coords = coordinates[3:6]  # x2, y2, z2
        arm3_coords = coordinates[6:9]  # x3, y3, z3

        # Add Z offset to each arm
        arm1_coords[2] += 150
        arm2_coords[2] += 150
        arm3_coords[2] += 150

        # Print parsed coordinates to terminal
        print(
            f"[PARSED] Arm1 coordinates: x={arm1_coords[0]:.2f}, y={arm1_coords[1]:.2f}, z={arm1_coords[2]:.2f}")
        print(
            f"[PARSED] Arm2 coordinates: x={arm2_coords[0]:.2f}, y={arm2_coords[1]:.2f}, z={arm2_coords[2]:.2f}")
        print(
            f"[PARSED] Arm3 coordinates: x={arm3_coords[0]:.2f}, y={arm3_coords[1]:.2f}, z={arm3_coords[2]:.2f}")

        # Coordinate clamping (keep within safe range)
        def clamp(x, min_val, max_val):
            return max(min(x, max_val), min_val)

        # Clamp each coordinate
        clamped_arm1 = [clamp(coord, -400, 400) for coord in arm1_coords]
        clamped_arm2 = [clamp(coord, -400, 400) for coord in arm2_coords]
        clamped_arm3 = [clamp(coord, -400, 400) for coord in arm3_coords]

        # Construct commands (using fixed t=3.14 and actual coordinates)
        arm1_command = f'{{"T":1041,"x":200,"y":{clamped_arm1[1]:.1f},"z":{clamped_arm1[2]:.1f},"t":3.14}}'
        arm2_command = f'{{"T":1041,"x":200,"y":{clamped_arm2[1]:.1f},"z":{clamped_arm2[2]:.1f},"t":3.14}}'
        arm3_command = f'{{"T":1041,"x":200,"y":{clamped_arm3[1]:.1f},"z":{clamped_arm3[2]:.1f},"t":3.14}}'

        # Print constructed JSON commands to terminal
        print(f"[COMMAND] Arm1 JSON: {arm1_command}")
        print(f"[COMMAND] Arm2 JSON: {arm2_command}")
        print(f"[COMMAND] Arm3 JSON: {arm3_command}")

        # Also log to file
        logger.info(f"Received from Unity: {position}")
        logger.info(
            f"Parsed coordinates - Arm1: x={arm1_coords[0]}, y={arm1_coords[1]}, z={arm1_coords[2]}")
        logger.info(
            f"Parsed coordinates - Arm2: x={arm2_coords[0]}, y={arm2_coords[1]}, z={arm2_coords[2]}")
        logger.info(
            f"Parsed coordinates - Arm3: x={arm3_coords[0]}, y={arm3_coords[1]}, z={arm3_coords[2]}")
        logger.info(f"Command for Arm1: {arm1_command}")
        logger.info(f"Command for Arm2: {arm2_command}")
        logger.info(f"Command for Arm3: {arm3_command}")

        # Directly send commands to respective robotic arms
        def send_to_arm(ip, cmd):
            result = send_command(ip, cmd)
            print(
                f"[SENT] Command to {ip}: {'Success' if result is not None else 'Failed'}")

        # Use threads to send simultaneously
        t1 = threading.Thread(target=send_to_arm, args=(ARM1_IP, arm1_command))
        t2 = threading.Thread(target=send_to_arm, args=(ARM2_IP, arm2_command))
        t3 = threading.Thread(target=send_to_arm, args=(ARM3_IP, arm3_command))

        t1.start()
        t2.start()
        t3.start()

        t1.join()
        t2.join()
        t3.join()

    except (IndexError, ValueError) as e:
        error_msg = f"Coordinate processing error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        logger.error(error_msg)


def main():
    host = '127.0.0.1'
    port = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(
        f"System initialized. Waiting for Unity connection on {host}:{port}...")
    print(f"Arm IPs: Arm1={ARM1_IP}, Arm2={ARM2_IP}, Arm3={ARM3_IP}")
    logger.info(
        f"System initialized. Waiting for Unity connection on {host}:{port}...")
    logger.info(f"Arm IPs: Arm1={ARM1_IP}, Arm2={ARM2_IP}, Arm3={ARM3_IP}")

    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")
    logger.info(f"Connection established with {client_address}")

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            position = data.decode('utf-8').strip()
            send_to_robot_arms(position)  # Process received coordinates
    except Exception as e:
        error_msg = f"System error: {str(e)}"
        print(f"[CRITICAL] {error_msg}")
        logger.error(error_msg)
    finally:
        client_socket.close()
        server_socket.close()
        print("Connection closed. System shutting down.")
        logger.info("Connection closed. System shutting down.")


if __name__ == "__main__":
    main()
