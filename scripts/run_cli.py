import sys
import os
import time
import argparse
import msvcrt

# Add src to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from obsbot_controller import ObsbotController, DEFAULT_IP, DEFAULT_PORT, DEFAULT_DEVICE_INDEX

# Prevent UTF-8 output errors on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

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
        
        char = msvcrt.getch().decode('utf-8', errors='ignore').lower()
        
        if char == 'q':
            print("Exiting program...")
            break
        elif char == 'w':
            current_tilt = max(-90.0, current_tilt - 5.0)
            controller.set_gimbal_degree(50.0, current_pan, current_tilt)
        elif char == 's':
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
                controller.set_ai_mode(0)
                time.sleep(0.1)
            controller.toggle_ai_lock(tracking_enabled)
        elif char == 'p':
            controller.take_snapshot()
            print("Photo taken!")
            time.sleep(0.5)
            
        time.sleep(0.05)

if __name__ == "__main__":
    main()
