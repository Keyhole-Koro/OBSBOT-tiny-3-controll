import sys
import msvcrt
import time
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
        """OBSBOT CenterへOSCメッセージを送信する"""
        self.client.send_message(address, list(arguments))

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
        """角度を指定して移動 (パン: -150〜150度, チルト: -90〜90度)"""
        # OBSBOT CenterはOSCの引数として整数(int)を要求するためキャストします
        self.send("/OBSBOT/WebCam/General/SetGimMotorDegree", self.device_index, int(speed), int(pan), int(tilt))

    def take_snapshot(self):
        """Pythonプログラム自身でカメラから映像を取得し、写真を保存する"""
        import cv2
        import datetime
        import os
        
        print("\nカメラから画像を取得中...")
        # DirectShowを使用してカメラを開く（Windows向け）
        cap = cv2.VideoCapture(self.device_index, cv2.CAP_DSHOW)
        
        if not cap.isOpened():
            # 通常の方法でフォールバック
            cap = cv2.VideoCapture(self.device_index)
            
        if not cap.isOpened():
            print("【エラー】カメラを開けませんでした。他のアプリ（カメラアプリ等）がカメラを使用中の可能性があります。")
            return

        # 露出やオートフォーカスを安定させるため数フレーム読み飛ばす
        for _ in range(5):
            cap.read()

        ret, frame = cap.read()
        if ret:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"obsbot_photo_{timestamp}.jpg"
            downloads_dir = os.path.expanduser("~\\Downloads")
            filepath = os.path.join(downloads_dir, filename)
            
            cv2.imwrite(filepath, frame)
            print(f"【成功】写真をプログラム側で保存しました: {filepath}")
        else:
            print("【エラー】画像を取得できませんでした。")
            
        cap.release()

def print_menu(pan, tilt, zoom, tracking):
    print("\033[H\033[J", end="") # 画面クリア
    print("==================================================")
    print("      OBSBOT キーボード コントローラー (16284ポート)")
    print("==================================================")
    print(f"  [現在のステータス]")
    print(f"    ・パン(左右)  : {pan:+.1f} 度 (A/Dキーで操作)")
    print(f"    ・チルト(上下): {tilt:+.1f} 度 (W/Sキーで操作)")
    print(f"    ・ズーム      : {zoom}% (I/Oキーで操作)")
    print(f"    ・追跡ロック  : {'ON' if tracking else 'OFF'} (Tキーでトグル)")
    print("--------------------------------------------------")
    print("  [操作キー一覧]")
    print("    W : 上に傾ける (チルト +5)")
    print("    S : 下に傾ける (チルト -5)")
    print("    A : 左に向ける (パン +10)")
    print("    D : 右に向ける (パン -10)")
    print("    I : ズームイン (+10%)")
    print("    O : ズームアウト (-10%)")
    print("    R : 首振りとズームをリセット")
    print("    T : 追跡(トラッキング)のON/OFF切り替え")
    print("    P : 写真（スナップショット）撮影")
    print("    Q : 終了")
    print("==================================================")
    print("操作したいキーを押してください...")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="OBSBOT Keyboard Controller")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="OBSBOT Centerの受信ポート")
    parser.add_argument("--ip", type=str, default=DEFAULT_IP, help="OBSBOT CenterのIPアドレス")
    parser.add_argument("--device", type=int, default=DEFAULT_DEVICE_INDEX, help="デバイス番号 (1台目なら0)")
    args = parser.parse_args()

    controller = ObsbotController(ip=args.ip, port=args.port, device_index=args.device)
    
    # 初期状態
    current_pan = 0.0
    current_tilt = 0.0
    current_zoom = 0
    tracking_enabled = False
    
    # 起動時の初期化
    controller.wake()
    controller.reset_gimbal()
    controller.set_zoom(0)
    controller.toggle_ai_lock(False)
    
    while True:
        print_menu(current_pan, current_tilt, current_zoom, tracking_enabled)
        
        # キー入力を待機 (msvcrtによりEnter不要で即時判定)
        char = msvcrt.getch().decode('utf-8', errors='ignore').lower()
        
        if char == 'q':
            print("プログラムを終了します...")
            break
        elif char == 'w':
            # カメラを上に向けるにはマイナスの角度にする必要があるためマイナス方向にします
            current_tilt = max(-90.0, current_tilt - 5.0)
            controller.set_gimbal_degree(50.0, current_pan, current_tilt)
        elif char == 's':
            # カメラを下に向けるにはプラスの角度にする必要があるためプラス方向にします
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
                controller.set_ai_mode(0) # 人物単独
                time.sleep(0.1)
            controller.toggle_ai_lock(tracking_enabled)
        elif char == 'p':
            controller.take_snapshot()
            print("写真を撮影しました！")
            time.sleep(0.5)
            
        time.sleep(0.05)

if __name__ == "__main__":
    main()
