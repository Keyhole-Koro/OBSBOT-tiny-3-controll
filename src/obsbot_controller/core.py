from pythonosc.tcp_client import SimpleTCPClient

class ObsbotController:
    def __init__(self, ip, port, device_index):
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

    def trigger_preset(self, preset_index: int):
        """Trigger preset (0~)"""
        self.send("/OBSBOT/WebCam/Tiny/TriggerPreset", self.device_index, preset_index)

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
            # Save in the current working directory
            current_dir = os.getcwd()
            filepath = os.path.join(current_dir, filename)
            
            cv2.imwrite(filepath, frame)
            print(f"[Success] Photo saved successfully by the program: {filepath}")
        else:
            print("[Error] Failed to grab frame.")
            
        cap.release()
