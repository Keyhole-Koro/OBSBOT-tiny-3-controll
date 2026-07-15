import argparse
import time
import sys
from pythonosc.tcp_client import SimpleTCPClient

# WindowsでUTF-8出力がエラーになるのを防ぐ
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

import os

def detect_ip():
    # WSL環境の場合は、WindowsホストのIPアドレスを取得する
    if os.path.exists('/proc/version'):
        try:
            with open('/proc/version', 'r') as f:
                if 'microsoft' in f.read().lower():
                    with open('/etc/resolv.conf', 'r') as resolv:
                        for line in resolv:
                            if line.strip().startswith('nameserver'):
                                host_ip = line.split()[1].strip()
                                print(f"WSL環境を検出しました。WindowsホストIP: {host_ip} を使用します。")
                                return host_ip
        except Exception:
            pass
    return "127.0.0.1"

# デフォルト設定 (OBSBOT Centerの設定に合わせて変更してください)
DEFAULT_IP = detect_ip()
DEFAULT_PORT = 16284  # OBSBOT CenterのOSC設定画面に表示された受信ポートに変更
DEFAULT_DEVICE_INDEX = 0

class ObsbotController:
    def __init__(self, ip=DEFAULT_IP, port=DEFAULT_PORT, device_index=DEFAULT_DEVICE_INDEX):
        self.ip = ip
        self.port = port
        self.device_index = device_index
        self.client = SimpleTCPClient(self.ip, self.port)
        print(f"Initialized OBSBOT Controller - IP: {self.ip}, Port: {self.port}, Device Index: {self.device_index}")

    def send(self, address: str, *arguments) -> None:
        """OBSBOT CenterへOSCメッセージを送信する"""
        self.client.send_message(address, list(arguments))
        print(f"Sent -> Address: {address}, Arguments: {arguments}")

    def wake(self):
        """カメラを起動"""
        self.send("/OBSBOT/WebCam/General/WakeSleep", self.device_index, 1)

    def sleep(self):
        """カメラをスリープ"""
        self.send("/OBSBOT/WebCam/General/WakeSleep", self.device_index, 0)

    def reset_gimbal(self):
        """ジンバルを中央へ戻す"""
        self.send("/OBSBOT/WebCam/General/ResetGimbal", self.device_index, 0)

    def set_zoom(self, zoom_level: int):
        """ズームを設定 (0〜100)"""
        self.send("/OBSBOT/WebCam/General/SetZoom", self.device_index, zoom_level)

    def set_ai_mode(self, mode: int):
        """AIモードを設定 (0:人物単独, 1:人物グループ, 2:音声, 3:デスク, 4:ハンド, 5:ホワイトボード)"""
        self.send("/OBSBOT/WebCam/Tiny/SetAiMode", self.device_index, mode)

    def toggle_ai_lock(self, lock: bool):
        """AI対象をロック/解除"""
        val = 1 if lock else 0
        self.send("/OBSBOT/WebCam/Tiny/ToggleAILock", self.device_index, val)

    def set_gimbal_degree(self, speed: float, pan: float, tilt: float):
        """角度を指定して移動"""
        self.send("/OBSBOT/WebCam/General/SetGimMotorDegree", self.device_index, int(speed), int(pan), int(tilt))

    def trigger_preset(self, preset_index: int):
        """プリセット呼び出し (0〜)"""
        self.send("/OBSBOT/WebCam/Tiny/TriggerPreset", self.device_index, preset_index)

    def take_snapshot(self):
        """スナップショット（写真）を撮影"""
        self.send("/OBSBOT/WebCam/General/PCSnapshot", self.device_index, 1)

def main():
    parser = argparse.ArgumentParser(description="OBSBOT Tiny 3 OSC Controller")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="OBSBOT CenterのOSC設定に表示された受信ポート")
    parser.add_argument("--ip", type=str, default=DEFAULT_IP, help="OBSBOT CenterのIPアドレス")
    parser.add_argument("--device", type=int, default=DEFAULT_DEVICE_INDEX, help="デバイス番号 (1台目なら0)")
    
    args = parser.parse_args()

    if args.port == 0:
        print("【警告】ポート番号が設定されていません。OBSBOT CenterのOSC設定画面でポート番号を確認し、引数で指定してください。")
        print("実行例: python obsbot_controller.py --port 12345")
        return

    controller = ObsbotController(ip=args.ip, port=args.port, device_index=args.device)

    # デモ用の動作シーケンス
    print("\n--- テスト動作を開始します ---")
    
    print("1. カメラを起動")
    controller.wake()
    time.sleep(2)

    print("2. ジンバルをリセット")
    controller.reset_gimbal()
    time.sleep(2)

    print("3. ズームを50%に設定")
    controller.set_zoom(50)
    time.sleep(2)

    print("3.5 写真（スナップショット）を撮影")
    controller.take_snapshot()
    time.sleep(2)

    print("4. 人物・単独トラッキングモードをオンにしてロック")
    controller.set_ai_mode(0)
    time.sleep(0.5)
    controller.toggle_ai_lock(True)
    time.sleep(3)
    
    print("5. トラッキングを解除してズームアウト、ジンバルリセット")
    controller.toggle_ai_lock(False)
    controller.set_zoom(0)
    controller.reset_gimbal()
    
    print("\n--- テスト完了 ---")

if __name__ == "__main__":
    main()
