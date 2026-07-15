import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from obsbot_controller import ObsbotController

@pytest.fixture
def mock_client():
    with patch('obsbot_controller.core.SimpleTCPClient') as MockClient:
        yield MockClient

@pytest.fixture
def controller(mock_client):
    ctrl = ObsbotController(ip="127.0.0.1", port=16284, device_index=0)
    ctrl.client.send_message = MagicMock()
    return ctrl

def test_wake(controller):
    controller.wake()
    controller.client.send_message.assert_called_once_with("/OBSBOT/WebCam/General/WakeSleep", [0, 1])

def test_sleep(controller):
    controller.sleep()
    controller.client.send_message.assert_called_once_with("/OBSBOT/WebCam/General/WakeSleep", [0, 0])

def test_reset_gimbal(controller):
    controller.reset_gimbal()
    controller.client.send_message.assert_called_once_with("/OBSBOT/WebCam/General/ResetGimbal", [0, 0])

def test_set_zoom(controller):
    controller.set_zoom(50)
    controller.client.send_message.assert_called_once_with("/OBSBOT/WebCam/General/SetZoom", [0, 50])

def test_set_ai_mode(controller):
    controller.set_ai_mode(2)
    controller.client.send_message.assert_called_once_with("/OBSBOT/WebCam/Tiny/SetAiMode", [0, 2])

def test_toggle_ai_lock(controller):
    controller.toggle_ai_lock(True)
    controller.client.send_message.assert_called_once_with("/OBSBOT/WebCam/Tiny/ToggleAILock", [0, 1])
    
    controller.toggle_ai_lock(False)
    controller.client.send_message.assert_called_with("/OBSBOT/WebCam/Tiny/ToggleAILock", [0, 0])

def test_set_gimbal_degree_casts_to_int(controller):
    controller.set_gimbal_degree(50.5, 10.9, -15.2)
    controller.client.send_message.assert_called_once_with("/OBSBOT/WebCam/General/SetGimMotorDegree", [0, 50, 10, -15])

def test_trigger_preset(controller):
    controller.trigger_preset(1)
    controller.client.send_message.assert_called_once_with("/OBSBOT/WebCam/Tiny/TriggerPreset", [0, 1])

@patch('cv2.VideoCapture')
@patch('cv2.imwrite')
def test_take_snapshot_osc(mock_imwrite, mock_videocapture, controller):
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.read.return_value = (True, "fake_frame_data")
    mock_videocapture.return_value = mock_cap

    controller.take_snapshot()
    mock_cap.release.assert_called_once()
    mock_imwrite.assert_called_once()
