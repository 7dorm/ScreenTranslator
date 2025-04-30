import torch

from typing import Union, Any

from torch.mps import device_count

from src.tools.models.common import AutoShape, Detections


class NNModel:
    """
    🔍 Neural Network Model 🔍
    """

    def __init__(self,
                 path: str,
                 language_code: str,
                 half_precision: bool = True) -> None:
        """
        Initialize YOLOv5 model with optimizations.

        :param path: Path to model

        :param language_code: Language code for pretrained model

        :param half_precision: Use half precision or not
        """

        # Model initialization
        self.model: AutoShape = torch.hub.load('ultralytics/yolov5',
                                               'custom',
                                               path=path,
                                               _verbose=False,
                                               device='mps')


        self.lang: str = language_code

        # Optimizations
        self.model.conf = 0.2  # Confidence threshold
        # self.model.dmb = True  # NMS IoU threshold
        # self.model.classes = None  # All classes
        self.model.iou = 0.3  # NMS IoU threshold
        self.model.agnostic = True  # NMS class-agnostic
        self.model.multi_label = False  # NMS multiple labels per box
        self.model.max_det = 3000  # maximum number of detections per image
        self.model.amp = True  # Automatic Mixed Precision (AMP) inference

        self.model.modules()
        self._USE_CUDA: bool = torch.cuda.is_available()
        self._USE_HALF_PRECISION: bool = half_precision
        if self._USE_CUDA:
            self.model.cuda()
        if self._USE_HALF_PRECISION:
            self.model.half()

    def __call__(self, data: Union[str, Any], size=1500) -> Detections:
        return self.model(data, size)
