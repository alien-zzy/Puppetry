# Introduction

Aims to combine the traditional Chinese intangible cultural heritage - shadow puppetry

Using virtual reality (VR) and robotic arm control technology to achieve an immersive interactive experience of "virtual control-reality restoration”

Through technological means, can make it easier for the younger generation to access and identify with traditional culture and promote the inheritance and innovation of intangible cultural heritage.


---

## 📦 Installation

```bash
git clone https://github.com/alien-zzy/Puppetry.git
cd your-repo

```
## 🎮 Project Features

- 🕶 ️VR perspective operation: users can freely manipulate shadow puppets in 3D virtual space
- 🧍 Virtual shadow puppet characters: highly realistic shadow puppet modeling and action binding.
- 🤖 Robotic arm synchronization: 3 robotic arms drive the physical shadow puppets to move synchronously through control signals.
- 🎭 Metaverse + Intangible Cultural Heritage: explore the integration and innovation of intangible cultural heritage and metaverse.

## 🧱 Technology Stack

- Unity（3D scenes and interactions）
- Oculus / SteamVR SDK（VR Controll）
- RoArm-M2-S (Rrobot Arm）
- Blender（Shadow puppet modeling and rigging）
- C# / Python（Script control and signal processing）

## ⚙️ Robotic Arm Setup

1. **Power on** the robotic arms.
2. Ensure the **robotic arms and your PC are connected to the same local network**.
3. Open the file:**. Puppetry/Python/RoboticArm.py** and set the correct **local IP address** for the robotic arms.
4. Run the Python script to establish the connection:
    ```bash
    python RoboticArm.py
    ```
5. Launch the Unity project and start the main VR scene.

## 🧪 Test Environment

The system has been tested under the following environment:

| Component         | Specification                           |
|------------------|------------------------------------------|
| Unity Version     | Unity 2022.3.47f1                        |
| VR Device         | Oculus Quest 2 + Link  |
| Robotic Arms      | RoArm-M2-S (waveshare)  |
| Control Interface | Python 3.9 + Serial / Socket LAN Control |
| OS                | Windows 10 / 11                          |

> ⚠️ Please ensure all devices are on the same LAN for real-time synchronization.

## 🔗 Meta Quest Link Setup

To run this VR project with **Meta Quest 2** via PC VR, follow these steps:

1. **Install Meta Quest Link (Oculus PC App)**  
   Download and install the Oculus app for Windows:  
   👉 [https://www.meta.com/quest/setup/](https://www.meta.com/quest/setup/)

2. **Enable Developer Mode** on your Quest device  
   - Open the **Meta Quest mobile app**  
   - Go to *Menu → Devices → Developer Mode → Enable*

3. **Connect Your Headset to PC**
   - Option 1: Use a **USB-C cable (Oculus Link)**
   - Option 2: Use **Air Link** (wirelessly, same LAN)

4. **Launch the Oculus PC App**
   - Go to *Settings → Beta → Enable Air Link* if using wireless
   - In your headset, confirm the connection by selecting **“Enable Link”**

5. **Ensure OpenXR Runtime is Set to Oculus**
   - In Oculus app: *Settings → General → Set Oculus as OpenXR Runtime*

6. **(Optional) Launch SteamVR**
   - SteamVR will automatically detect Oculus runtime

7. **Run the Unity Project**
   - Open Unity and enter Play Mode

