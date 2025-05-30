import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
import numpy as np

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from ScreenTranslator.tools.MPCustom import CustomImage, CustomVideo

def mock_process_function(input_data):
    result = MagicMock()
    result.frame = "dummy_frame"
    result.text = "recognized"
    result.translated = "translated"
    return result

def test_custom_image_initialization():
    """Test that CustomImage stores the result correctly."""
    dummy_path = "dummy_path.jpg"
    image = CustomImage(dummy_path, mock_process_function)
    
    assert image.result.frame == "dummy_frame"
    assert image.result.text == "recognized"
    assert image.result.translated == "translated"

def test_custom_video_initialization():
    """Test that CustomVideo initializes correctly."""
    dummy_path = "dummy_path.mp4"
    video = CustomVideo(dummy_path, mock_process_function)
    
    assert hasattr(video, 'cap')
    assert video.loaded in [True, False]

@patch('cv2.VideoCapture')
def test_custom_video_iteration(mock_videocapture):
    """Test CustomVideo iteration with mock."""
    # Настраиваем mock
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.read.side_effect = [
        (True, np.zeros((100, 100, 3))),  # Первый кадр
        (False, None)  # Конец видео
    ]
    mock_videocapture.return_value = mock_cap
    
    video = CustomVideo("dummy.mp4", mock_process_function)
    
    # Первый кадр
    result = next(video)
    assert result.frame == "dummy_frame"
    
    # Конец видео
    with pytest.raises(StopIteration):
        next(video)