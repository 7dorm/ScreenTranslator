import pytest
from src.tools.MPCustom import CustomImage, CustomVideo


class DummyResult:
    def __init__(self):
        self.frame = "dummy_frame"
        self.text = "recognized"
        self.translated = "translated"


def test_custom_image_initialization():
    """Test that CustomImage stores the result correctly."""
    dummy_result = DummyResult()
    image = CustomImage(dummy_result)

    assert image.result.frame == "dummy_frame"
    assert image.result.text == "recognized"
    assert image.result.translated == "translated"


def test_custom_video_initialization():
    """Test that CustomVideo stores the result correctly."""
    dummy_result = DummyResult()
    video = CustomVideo(dummy_result)

    assert video.result.frame == "dummy_frame"
    assert video.result.text == "recognized"
    assert video.result.translated == "translated"