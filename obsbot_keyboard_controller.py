import sys
import msvcrt
import time
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

DEFAULT_IP = detect_ip()
DEFAULT_PORT = 16284
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
        """Move gimbal by specified angle (Pan: -150 to 150, Tilt: -90 to 90)"""
        # OBSBOT Center requires integers (int) for OSC arguments, so we cast them
        self.send("/OBSBOT/WebCam/General/SetGimMotorDegree", self.device_index, int(speed), int(pan), int(tilt))

    def take_snapshot(self):
        """Capture image from the camera and save it within the Python program"""
        import cv2
        import datetime
        import os
        
        print("\nCapturing image from the camera...")
        # Open camera using DirectShow (for Windows)
        cap = cv2.VideoCapture(self.device_index, cv2.CAP_DSHOW)
        
        if not cap.isOpened():
            # Fallback to the standard method
            cap = cv2.VideoCapture(self.device_index)
            
        if not cap.isOpened():
            print("[Error] Failed to open camera. It might be in use by another application (like the Camera app).")
            return

        # Skip a few frames to stabilize exposure and autofocus
        for _ in range(5):
            cap.read()

        ret, frame = cap.read()
        if ret:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"obsbot_photo_{timestamp}.jpg"
            # Save in the same directory as the script (within the repository)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(current_dir, filename)
            
            cv2.imwrite(filepath, frame)
            print(f"[Success] Photo saved successfully by the program: {filepath}")
        else:
            print("[Error] Failed to grab frame.")
            
        cap.release()

def print_menu(pan, tilt, zoom, tracking):
    print("\033[H\033[J", end="") # Clear screen
    print("==================================================")
    print("      OBSBOT Keyboard Controller (Port 16284)")
    print("==================================================")
    print(f"  [Current Status]")
    print(f"    - Pan (L/R) : {pan:+.1f} degrees (A/D keys)")
    print(f"    - Tilt (U/D): {tilt:+.1f} degrees (W/S keys)")
    print(f"    - Zoom      : {zoom}% (I/O keys)")
    print(f"    - Tracking  : {'ON' if tracking else 'OFF'} (T key to toggle)")
    print("--------------------------------------------------")
    print("  [Controls]")
    print("    W : Tilt up (-5)")
    print("    S : Tilt down (+5)")
    print("    A : Pan left (+10)")
    print("    D : Pan right (-10)")
    print("    I : Zoom in (+10%)")
    print("    O : Zoom out (-10%)")
    print("    R : Reset gimbal and zoom")
    print("    T : Toggle AI tracking ON/OFF")
    print("    P : Take snapshot (Photo)")
    print("    Q : Quit")
    print("==================================================")
    print("Press a key to control...")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="OBSBOT Keyboard Controller")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="OBSBOT Center receive port")
    parser.add_argument("--ip", type=str, default=DEFAULT_IP, help="OBSBOT Center IP address")
    parser.add_argument("--device", type=int, default=DEFAULT_DEVICE_INDEX, help="Device index (0 for first camera)")
    args = parser.parse_args()

    controller = ObsbotController(ip=args.ip, port=args.port, device_index=args.device)
    
    # Initial state
    current_pan = 0.0
    current_tilt = 0.0
    current_zoom = 0
    tracking_enabled = False
    
    # Initialization on startup
    controller.wake()
    controller.reset_gimbal()
    controller.set_zoom(0)
    controller.toggle_ai_lock(False)
    
    while True:
        print_menu(current_pan, current_tilt, current_zoom, tracking_enabled)
        
        # Wait for key press (msvcrt gets key immediately without Enter)
        char = msvcrt.getch().decode('utf-8', errors='ignore').lower()
        
        if char == 'q':
            print("Exiting program...")
            break
        elif char == 'w':
            # Tilt up requires negative angle
            current_tilt = max(-90.0, current_tilt - 5.0)
            controller.set_gimbal_degree(50.0, current_pan, current_tilt)
        elif char == 's':
            # Tilt down requires positive angle
            current_tilt = min(90.0, current_tilt + 5.0)
            controller.set_gimbal_degree(50.0, current_pan, current_tilt)
        elif char == 'a':
            current_pan = min(150.0, current_pan + 10.0)
            controller.set_gimbal_degree(50.0, current_pan, current_tilt)
        elif char == 'd':
            current_pan = max(-150.0, current_pan - 10.0)
            controller.set_gimbal_degree(50.0, current_pan, current_tilt)
        elif char == 'i':
            current_zoom = min(100, current_zoom + 10)
            controller.set_zoom(current_zoom)
        elif char == 'o':
            current_zoom = max(0, current_zoom - 10)
            controller.set_zoom(current_zoom)
        elif char == 'r':
            current_pan = 0.0
            current_tilt = 0.0
            current_zoom = 0
            controller.reset_gimbal()
            controller.set_zoom(0)
        elif char == 't':
            tracking_enabled = not tracking_enabled
            if tracking_enabled:
                controller.set_ai_mode(0) # Single person
                time.sleep(0.1)
            controller.toggle_ai_lock(tracking_enabled)
        elif char == 'p':
            controller.take_snapshot()
            print("Photo taken!")
            time.sleep(0.5)
            
        time.sleep(0.05)

if __name__ == "__main__":
    main()
