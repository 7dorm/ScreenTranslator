import torch

from typing import Union, Any
from src.tools import AutoShape, Detections


class NNModel:
    """
    🔍 Neural Network Model 🔍
    """

    def __init__(self,
                 path: str,
                 language_code: str,
                 half_precision: bool =False) -> None:
        """
        Initialize YOLOv5 model with optimizations.

        :param path: Path to model

        :param language_code: Language code for pretrained model

        :param half_precision: Use half precision or not
        """

        # Model initialization
        self.model: AutoShape = torch.hub.load('ultralytics/yolov5', 'custom', path=path)
        self.lang: str = language_code

        # Optimizations
        self.model.conf = 0.5  # Confidence threshold
        self.model.iou = 0.45  # NMS IoU threshold
        self.model.classes = None  # All classes

        self._USE_CUDA: bool = torch.cuda.is_available()
        self._USE_HALF_PRECISION: bool = half_precision
        if self._USE_CUDA:
            self.model.cuda()
            if self._USE_HALF_PRECISION:
                self.model.half()

    def __call__(self, data: Union[str, Any]) -> Detections:
        return self.model(data)
