import sys
import os
import time
import argparse

# Add src to python path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from obsbot_controller import ObsbotController, DEFAULT_IP, DEFAULT_PORT, DEFAULT_DEVICE_INDEX

# Prevent UTF-8 output errors on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

def main():
    parser = argparse.ArgumentParser(description="OBSBOT Tiny 3 OSC Controller Demo")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Receive port displayed in OBSBOT Center OSC settings")
    parser.add_argument("--ip", type=str, default=DEFAULT_IP, help="OBSBOT Center IP address")
    parser.add_argument("--device", type=int, default=DEFAULT_DEVICE_INDEX, help="Device index (0 for the first camera)")
    
    args = parser.parse_args()

    if args.port == 0:
        print("[Warning] Port number is not set. Please check the port number on the OSC settings screen of OBSBOT Center and specify it as an argument.")
        print("Example: python run_demo.py --port 16284")
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
