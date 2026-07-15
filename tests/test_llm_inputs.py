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

def test_llm_string_inputs(controller):
    """Test that the controller handles string and float inputs from an LLM correctly."""
    
    # Test set_zoom with string and float
    controller.set_zoom("50")
    controller.client.send_message.assert_called_with("/OBSBOT/WebCam/General/SetZoom", [0, 50])
    
    controller.set_zoom("50.5")
    controller.client.send_message.assert_called_with("/OBSBOT/WebCam/General/SetZoom", [0, 50])

    # Test set_ai_mode with string
    controller.set_ai_mode("2")
    controller.client.send_message.assert_called_with("/OBSBOT/WebCam/Tiny/SetAiMode", [0, 2])

    # Test set_gimbal_degree with strings representing floats
    controller.set_gimbal_degree("50", "-15.5", "10.9")
    controller.client.send_message.assert_called_with("/OBSBOT/WebCam/General/SetGimMotorDegree", [0, 50, -15, 10])

    # Test trigger_preset with string
    controller.trigger_preset("1")
    controller.client.send_message.assert_called_with("/OBSBOT/WebCam/Tiny/TriggerPreset", [0, 1])

def test_llm_boolean_inputs(controller):
    """Test that toggle_ai_lock handles string booleans properly."""
    
    # Test "true"
    controller.toggle_ai_lock("true")
    controller.client.send_message.assert_called_with("/OBSBOT/WebCam/Tiny/ToggleAILock", [0, 1])
    
    # Test "false"
    controller.toggle_ai_lock("false")
    controller.client.send_message.assert_called_with("/OBSBOT/WebCam/Tiny/ToggleAILock", [0, 0])
    
    # Test "1"
    controller.toggle_ai_lock("1")
    controller.client.send_message.assert_called_with("/OBSBOT/WebCam/Tiny/ToggleAILock", [0, 1])

    # Test actual boolean
    controller.toggle_ai_lock(True)
    controller.client.send_message.assert_called_with("/OBSBOT/WebCam/Tiny/ToggleAILock", [0, 1])
