import argparse
import time
import sys
from pythonosc.tcp_client import SimpleTCPClient

# Prevent UTF-8 output errors on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

import os

def detect_ip():
    # If in WSL environment, get the Windows host IP address
    if os.path.exists('/proc/version'):
        try:
            with open('/proc/version', 'r') as f:
                if 'microsoft' in f.read().lower():
                    with open('/etc/resolv.conf', 'r') as resolv:
                        for line in resolv:
                            if line.strip().startswith('nameserver'):
                                host_ip = line.split()[1].strip()
                                print(f"WSL environment detected. Using Windows host IP: {host_ip}")
                                return host_ip
        except Exception:
            pass
    return "127.0.0.1"

# Default settings (change according to OBSBOT Center settings)
DEFAULT_IP = detect_ip()
DEFAULT_PORT = 16284  # Change to the receive port displayed on the OSC settings screen of OBSBOT Center
DEFAULT_DEVICE_INDEX = 0

class ObsbotController:
    def __init__(self, ip=DEFAULT_IP, port=DEFAULT_PORT, device_index=DEFAULT_DEVICE_INDEX):
        self.ip = ip
        self.port = port
        self.device_index = device_index
        self.client = SimpleTCPClient(self.ip, self.port)
        print(f"Initialized OBSBOT Controller - IP: {self.ip}, Port: {self.port}, Device Index: {self.device_index}")

    def send(self, address: str, *arguments) -> None:
        """Send OSC message to OBSBOT Center"""
        self.client.send_message(address, list(arguments))
        print(f"Sent -> Address: {address}, Arguments: {arguments}")

    def wake(self):
        """Wake camera"""
        self.send("/OBSBOT/WebCam/General/WakeSleep", self.device_index, 1)

    def sleep(self):
        """Sleep camera"""
        self.send("/OBSBOT/WebCam/General/WakeSleep", self.device_index, 0)

    def reset_gimbal(self):
        """Reset gimbal to center"""
        self.send("/OBSBOT/WebCam/General/ResetGimbal", self.device_index, 0)

    def set_zoom(self, zoom_level: int):
        """Set zoom (0 to 100)"""
        self.send("/OBSBOT/WebCam/General/SetZoom", self.device_index, zoom_level)

    def set_ai_mode(self, mode: int):
        """Set AI mode (0: Single Person, 1: Group, 2: Audio, 3: Desk, 4: Hand, 5: Whiteboard)"""
        self.send("/OBSBOT/WebCam/Tiny/SetAiMode", self.device_index, mode)

    def toggle_ai_lock(self, lock: bool):
        """Lock/unlock AI target"""
        val = 1 if lock else 0
        self.send("/OBSBOT/WebCam/Tiny/ToggleAILock", self.device_index, val)

    def set_gimbal_degree(self, speed: float, pan: float, tilt: float):
        """Move gimbal by specified angle"""
        self.send("/OBSBOT/WebCam/General/SetGimMotorDegree", self.device_index, int(speed), int(pan), int(tilt))

    def trigger_preset(self, preset_index: int):
        """Trigger preset (0~)"""
        self.send("/OBSBOT/WebCam/Tiny/TriggerPreset", self.device_index, preset_index)

    def take_snapshot(self):
        """Take a snapshot (photo)"""
        self.send("/OBSBOT/WebCam/General/PCSnapshot", self.device_index, 1)

def main():
    parser = argparse.ArgumentParser(description="OBSBOT Tiny 3 OSC Controller")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Receive port displayed in OBSBOT Center OSC settings")
    parser.add_argument("--ip", type=str, default=DEFAULT_IP, help="OBSBOT Center IP address")
    parser.add_argument("--device", type=int, default=DEFAULT_DEVICE_INDEX, help="Device index (0 for the first camera)")
    
    args = parser.parse_args()

    if args.port == 0:
        print("[Warning] Port number is not set. Please check the port number on the OSC settings screen of OBSBOT Center and specify it as an argument.")
        print("Example: python obsbot_controller.py --port 12345")
        return

    controller = ObsbotController(ip=args.ip, port=args.port, device_index=args.device)

    # Demo test sequence
    print("\n--- Starting test sequence ---")
    
    print("1. Wake camera")
    controller.wake()
    time.sleep(2)

    print("2. Reset gimbal")
    controller.reset_gimbal()
    time.sleep(2)

    print("3. Set zoom to 50%")
    controller.set_zoom(50)
    time.sleep(2)

    print("3.5 Take snapshot")
    controller.take_snapshot()
    time.sleep(2)

    print("4. Turn on and lock single person tracking mode")
    controller.set_ai_mode(0)
    time.sleep(0.5)
    controller.toggle_ai_lock(True)
    time.sleep(3)
    
    print("5. Unlock tracking, zoom out, reset gimbal")
    controller.toggle_ai_lock(False)
    controller.set_zoom(0)
    controller.reset_gimbal()
    
    print("\n--- Test complete ---")

if __name__ == "__main__":
    main()
