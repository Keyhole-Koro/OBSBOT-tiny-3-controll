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
