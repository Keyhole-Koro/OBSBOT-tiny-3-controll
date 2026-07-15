# OBSBOT Tiny 3 Controller

Python scripts to control the OBSBOT Tiny 3 over OSC (TCP).

## Installation

```bash
pip install -r requirements.txt
```

## Project Structure

```text
OBSBOT-tiny-3-controll/
├── src/
│   └── obsbot_controller/
│       ├── __init__.py
│       ├── core.py          # Core OBSBOT control logic
│       └── utils.py         # Utilities like IP detection
├── scripts/
│   ├── run_cli.py           # Keyboard interactive controller
│   ├── run_mcp.py           # MCP server for AI integration
│   └── run_demo.py          # Automated test sequence
├── tests/
│   └── test_core.py         # Pytest cases
```

## Usage

### 1. Interactive Keyboard Controller
Run the interactive CLI to control the camera with your keyboard (W/S/A/D to move, I/O to zoom, etc.).
```bash
python scripts/run_cli.py
```
*(Optional args: `--port 16284 --ip 127.0.0.1 --device 0`)*

### 2. Automated Demo
Run a predefined test sequence (wake up, reset, zoom, snapshot, tracking on/off).
```bash
python scripts/run_demo.py
```

### 3. MCP Server (For AI Integration)
Run the MCP server to allow AI assistants (like Claude Desktop or Cursor) to control the camera.
```bash
python scripts/run_mcp.py
```
