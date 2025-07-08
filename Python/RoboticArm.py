import socket
import requests
import threading
import json
import time
import tkinter as tk
from tkinter import ttk, filedialog
from queue import Queue

# Hardcoded IP addresses for three robotic arms
ARM1_IP = "192.168.43.6"  # First robotic arm IP
ARM2_IP = "192.168.43.111"  # Second robotic arm IP
ARM3_IP = "192.168.43.53"  # Third robotic arm IP


class RoboticArmControl:
    def __init__(self, root):
        self.root = root
        self.root.title("Robotic Arm Control System")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        # Create queues for thread communication
        self.path_queue = Queue()

        # State variables
        self.realtime_running = False
        self.path_playing = False
        self.realtime_thread = None
        self.server_socket = None

        # Create GUI
        self.create_widgets()

    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Status tab
        self.status_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.status_frame, text="Status")
        self.create_status_tab()

        # Control tab
        self.control_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.control_frame, text="Control")
        self.create_control_tab()

        # Path tab
        self.path_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.path_frame, text="Path")
        self.create_path_tab()

    def create_status_tab(self):
        # Arm information section
        arm_frame = ttk.LabelFrame(
            self.status_frame, text="Robotic Arms Information")
        arm_frame.pack(fill='x', padx=10, pady=10)

        # Arm 1 info
        ttk.Label(arm_frame, text="Arm 1:").grid(
            row=0, column=0, sticky='w', padx=5, pady=2)
        self.arm1_ip = ttk.Label(arm_frame, text=ARM1_IP)
        self.arm1_ip.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        self.arm1_status = ttk.Label(arm_frame, text="Disconnected")
        self.arm1_status.grid(row=0, column=2, sticky='w', padx=5, pady=2)

        # Arm 2 info
        ttk.Label(arm_frame, text="Arm 2:").grid(
            row=1, column=0, sticky='w', padx=5, pady=2)
        self.arm2_ip = ttk.Label(arm_frame, text=ARM2_IP)
        self.arm2_ip.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        self.arm2_status = ttk.Label(arm_frame, text="Disconnected")
        self.arm2_status.grid(row=1, column=2, sticky='w', padx=5, pady=2)

        # Arm 3 info
        ttk.Label(arm_frame, text="Arm 3:").grid(
            row=2, column=0, sticky='w', padx=5, pady=2)
        self.arm3_ip = ttk.Label(arm_frame, text=ARM3_IP)
        self.arm3_ip.grid(row=2, column=1, sticky='w', padx=5, pady=2)
        self.arm3_status = ttk.Label(arm_frame, text="Disconnected")
        self.arm3_status.grid(row=2, column=2, sticky='w', padx=5, pady=2)

        # Connection status section
        status_frame = ttk.LabelFrame(self.status_frame, text="System Status")
        status_frame.pack(fill='x', padx=10, pady=10)

        # Real-time control status
        ttk.Label(status_frame, text="Realtime Control:").grid(
            row=0, column=0, sticky='w', padx=5, pady=2)
        self.realtime_status = ttk.Label(status_frame, text="Stopped")
        self.realtime_status.grid(row=0, column=1, sticky='w', padx=5, pady=2)

        # Path replay status
        ttk.Label(status_frame, text="Path Replay:").grid(
            row=1, column=0, sticky='w', padx=5, pady=2)
        self.path_status = ttk.Label(status_frame, text="Inactive")
        self.path_status.grid(row=1, column=1, sticky='w', padx=5, pady=2)

    def create_control_tab(self):
        # Realtime control section
        realtime_frame = ttk.LabelFrame(
            self.control_frame, text="Real-time Control")
        realtime_frame.pack(fill='x', padx=10, pady=10)

        # Start/Stop realtime control
        self.realtime_btn = ttk.Button(realtime_frame, text="Start Real-time Control",
                                       command=self.toggle_realtime)
        self.realtime_btn.pack(pady=5)

        # Coordinates display
        coord_frame = ttk.LabelFrame(
            self.control_frame, text="Current Coordinates")
        coord_frame.pack(fill='x', padx=10, pady=10)

        # Arm 1 coordinates
        ttk.Label(coord_frame, text="Arm 1:").grid(
            row=0, column=0, sticky='w', padx=5, pady=2)
        self.arm1_coords = ttk.Label(coord_frame, text="x:0.0, y:0.0, z:0.0")
        self.arm1_coords.grid(row=0, column=1, sticky='w', padx=5, pady=2)

        # Arm 2 coordinates
        ttk.Label(coord_frame, text="Arm 2:").grid(
            row=1, column=0, sticky='w', padx=5, pady=2)
        self.arm2_coords = ttk.Label(coord_frame, text="x:0.0, y:0.0, z:0.0")
        self.arm2_coords.grid(row=1, column=1, sticky='w', padx=5, pady=2)

        # Arm 3 coordinates
        ttk.Label(coord_frame, text="Arm 3:").grid(
            row=2, column=0, sticky='w', padx=5, pady=2)
        self.arm3_coords = ttk.Label(coord_frame, text="x:0.0, y:0.0, z:0.0")
        self.arm3_coords.grid(row=2, column=1, sticky='w', padx=5, pady=2)

    def create_path_tab(self):
        # Path replay section
        path_frame = ttk.LabelFrame(self.path_frame, text="Path Replay")
        path_frame.pack(fill='x', padx=10, pady=10)

        # Load path button
        ttk.Button(path_frame, text="Load Path",
                   command=self.load_path).pack(pady=5)

        # Path status
        self.path_info = ttk.Label(path_frame, text="No path loaded")
        self.path_info.pack(pady=5)

        # Play/Stop buttons
        btn_frame = ttk.Frame(path_frame)
        btn_frame.pack(pady=5)

        self.play_btn = ttk.Button(btn_frame, text="Play Path",
                                   command=self.start_path_playback, state='disabled')
        self.play_btn.pack(side='left', padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="Stop Path",
                                   command=self.stop_path_playback, state='disabled')
        self.stop_btn.pack(side='left', padx=5)

        # Path progress
        self.progress_frame = ttk.Frame(path_frame)
        self.progress_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(self.progress_frame, text="Progress:").pack(anchor='w')
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient='horizontal',
                                            mode='determinate', variable=self.progress_var)
        self.progress_bar.pack(fill='x', pady=5)

    def toggle_realtime(self):
        if not self.realtime_running:
            # Start realtime control
            self.realtime_running = True
            self.realtime_status.config(text="Running")
            self.realtime_btn.config(text="Stop Real-time Control")

            # Start realtime server thread
            self.realtime_thread = threading.Thread(
                target=self.start_realtime_server, daemon=True)
            self.realtime_thread.start()
        else:
            # Stop realtime control
            self.realtime_running = False
            self.realtime_status.config(text="Stopped")
            self.realtime_btn.config(text="Start Real-time Control")

            # Close server socket to stop the thread
            if self.server_socket:
                try:
                    self.server_socket.close()
                except:
                    pass

    def load_path(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")])
        if not file_path:
            return

        try:
            with open(file_path, 'r') as f:
                path_data = json.load(f)

            if "frames" not in path_data:
                self.path_info.config(text="Invalid JSON format")
                return

            # Clear existing path
            while not self.path_queue.empty():
                self.path_queue.get()

            # Queue all frames
            for frame in path_data["frames"]:
                self.path_queue.put(frame)

            self.path_info.config(
                text=f"Loaded {self.path_queue.qsize()} frames")
            self.play_btn.config(state='normal')
            self.stop_btn.config(state='normal')
            self.progress_var.set(0)

        except Exception as e:
            self.path_info.config(text=f"Error loading file: {str(e)}")

    def start_path_playback(self):
        if self.path_queue.empty():
            return

        self.path_playing = True
        self.path_status.config(text="Playing")
        self.path_play_thread = threading.Thread(
            target=self.play_path, daemon=True)
        self.path_play_thread.start()

    def stop_path_playback(self):
        self.path_playing = False
        self.path_status.config(text="Stopped")

    def play_path(self):
        total_frames = self.path_queue.qsize()
        processed = 0

        while self.path_playing and not self.path_queue.empty():
            frame = self.path_queue.get()

            # Construct position string for send_to_robot_arms
            position = (
                f"{frame['armOne_x']},{frame['armOne_y']},{frame['armOne_z']},"
                f"{frame['armTwo_x']},{frame['armTwo_y']},{frame['armTwo_z']},"
                f"{frame['Head_x']},{frame['Head_y']},{frame['Head_z']}"
            )

            # Send to robotic arms
            self.send_to_robot_arms(position)

            # Update UI
            processed += 1
            progress = int((processed / total_frames) * 100)
            self.root.after(0, lambda: self.progress_var.set(progress))

            # Wait for next frame
            time.sleep(0.005)  # 5ms interval

        self.path_playing = False
        self.root.after(0, lambda: self.path_status.config(
            text="Completed" if self.path_queue.empty() else "Stopped"))

    def start_realtime_server(self):
        host = '127.0.0.1'
        port = 12345

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(1)
        # Set timeout to allow checking for shutdown
        self.server_socket.settimeout(1)

        self.root.after(
            0, lambda: self.realtime_status.config(text="Listening..."))

        while self.realtime_running:
            try:
                client_socket, client_address = self.server_socket.accept()
                client_socket.settimeout(0.1)

                self.root.after(
                    0, lambda: self.realtime_status.config(text="Connected"))

                while self.realtime_running:
                    try:
                        data = client_socket.recv(1024)
                        if not data:
                            break

                        position = data.decode('utf-8').strip()
                        self.send_to_robot_arms(position)

                        # Update coordinates display
                        try:
                            coords = [float(x) for x in position.split(',')]
                            if len(coords) >= 9:
                                self.root.after(0, lambda: self.arm1_coords.config(
                                    text=f"x:{coords[0]:.1f}, y:{coords[1]:.1f}, z:{coords[2]:.1f}"))
                                self.root.after(0, lambda: self.arm2_coords.config(
                                    text=f"x:{coords[3]:.1f}, y:{coords[4]:.1f}, z:{coords[5]:.1f}"))
                                self.root.after(0, lambda: self.arm3_coords.config(
                                    text=f"x:{coords[6]:.1f}, y:{coords[7]:.1f}, z:{coords[8]:.1f}"))
                        except Exception:
                            pass

                    except socket.timeout:
                        continue
                    except ConnectionResetError:
                        break

                client_socket.close()

            except socket.timeout:
                continue
            except OSError:
                # Socket closed externally
                break

        # Clean up when stopping
        try:
            self.server_socket.close()
        except:
            pass
        self.server_socket = None

    def send_command(self, ip, command):
        """Send a single command to the robotic arm at the specified IP"""
        try:
            url = f"http://{ip}/js?json={command}"
            response = requests.get(url, timeout=3)

            # Update status based on response
            status_text = "Connected" if response.status_code == 200 else "Error"
            if ip == ARM1_IP:
                self.root.after(
                    0, lambda: self.arm1_status.config(text=status_text))
            elif ip == ARM2_IP:
                self.root.after(
                    0, lambda: self.arm2_status.config(text=status_text))
            elif ip == ARM3_IP:
                self.root.after(
                    0, lambda: self.arm3_status.config(text=status_text))

            return response.text
        except requests.RequestException:
            if ip == ARM1_IP:
                self.root.after(
                    0, lambda: self.arm1_status.config(text="Disconnected"))
            elif ip == ARM2_IP:
                self.root.after(
                    0, lambda: self.arm2_status.config(text="Disconnected"))
            elif ip == ARM3_IP:
                self.root.after(
                    0, lambda: self.arm3_status.config(text="Disconnected"))
            return None

    def send_to_robot_arms(self, position):
        """Receive coordinates and send to three robotic arms"""
        try:
            # Split coordinate string into 9 values (three points, each x,y,z)
            coordinates = [float(coord) for coord in position.split(',')]
            if len(coordinates) != 9:
                return

            # Parse coordinates for each robotic arm
            arm1_coords = coordinates[0:3]  # x1, y1, z1
            arm2_coords = coordinates[3:6]  # x2, y2, z2
            arm3_coords = coordinates[6:9]  # x3, y3, z3

            # Add Z offset to each arm
            arm1_coords[2] += 150
            arm2_coords[2] += 150
            arm3_coords[2] += 150

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

            # Directly send commands to respective robotic arms
            def send_to_arm(ip, cmd):
                self.send_command(ip, cmd)

            # Use threads to send simultaneously
            t1 = threading.Thread(target=send_to_arm,
                                  args=(ARM1_IP, arm1_command))
            t2 = threading.Thread(target=send_to_arm,
                                  args=(ARM2_IP, arm2_command))
            t3 = threading.Thread(target=send_to_arm,
                                  args=(ARM3_IP, arm3_command))

            t1.start()
            t2.start()
            t3.start()

            t1.join()
            t2.join()
            t3.join()

        except (IndexError, ValueError):
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app = RoboticArmControl(root)

    # 修复窗口关闭处理

    def on_closing():
        app.realtime_running = False  # 停止实时控制
        app.path_playing = False  # 停止路径回放
        if app.server_socket:
            try:
                app.server_socket.close()
            except:
                pass
        root.destroy()
        exit(0)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
