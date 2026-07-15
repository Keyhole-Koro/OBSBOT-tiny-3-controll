import sys
import argparse
from mcp.server.fastmcp import FastMCP
from obsbot_controller import ObsbotController, DEFAULT_IP, DEFAULT_PORT, DEFAULT_DEVICE_INDEX

mcp = FastMCP("OBSBOT Tiny 3 Controller")
controller = None

@mcp.tool()
def wake_camera() -> str:
    """Wake the OBSBOT camera from sleep."""
    controller.wake()
    return "Camera awakened."

@mcp.tool()
def sleep_camera() -> str:
    """Put the OBSBOT camera to sleep."""
    controller.sleep()
    return "Camera is now sleeping."

@mcp.tool()
def reset_gimbal() -> str:
    """Reset the gimbal to its center position."""
    controller.reset_gimbal()
    return "Gimbal reset to center."

@mcp.tool()
def set_zoom(zoom_level: int) -> str:
    """Set the zoom level (0 to 100)."""
    controller.set_zoom(zoom_level)
    return f"Zoom set to {zoom_level}%."

@mcp.tool()
def set_gimbal_degree(speed: float, pan: float, tilt: float) -> str:
    """Move gimbal by specified angle.
    Pan: -150 to 150 (positive is left, negative is right)
    Tilt: -90 to 90 (negative is up, positive is down)
    Speed: 0 to 100
    """
    controller.set_gimbal_degree(speed, pan, tilt)
    return f"Gimbal moved (Pan: {pan}, Tilt: {tilt}, Speed: {speed})."

@mcp.tool()
def set_ai_mode(mode: int) -> str:
    """Set AI tracking mode (0: Single Person, 1: Group, 2: Audio, 3: Desk, 4: Hand, 5: Whiteboard)."""
    controller.set_ai_mode(mode)
    return f"AI mode set to {mode}."

@mcp.tool()
def toggle_ai_lock(lock: bool) -> str:
    """Lock or unlock AI target tracking."""
    controller.toggle_ai_lock(lock)
    return "AI tracking locked." if lock else "AI tracking unlocked."

@mcp.tool()
def take_snapshot() -> str:
    """Take a snapshot and save it."""
    controller.take_snapshot()
    return "Snapshot taken and saved."

def main():
    global controller
    # Only parse args if they are passed, otherwise use defaults
    # MCP hosts might pass additional unknown arguments, so we use parse_known_args
    parser = argparse.ArgumentParser(description="OBSBOT Tiny 3 MCP Server")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="OBSBOT Center receive port")
    parser.add_argument("--ip", type=str, default=DEFAULT_IP, help="OBSBOT Center IP address")
    parser.add_argument("--device", type=int, default=DEFAULT_DEVICE_INDEX, help="Device index (0 for first camera)")
    args, _ = parser.parse_known_args()

    controller = ObsbotController(ip=args.ip, port=args.port, device_index=args.device)
    
    # FastMCP uses stdio by default when mcp.run() is called
    mcp.run()

if __name__ == "__main__":
    main()
