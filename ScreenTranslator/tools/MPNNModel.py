import torch

from typing import Union, Any
from ScreenTranslator.constants import *

class NNModel:
    """
    🔍 Neural Network Model 🔍
    """

    def __init__(self,
                 path: str,
                 language_code: str,
                 params = None) -> None:
        """
        Initialize YOLOv5 model with optimizations.

        :param path: Path to model

        :param language_code: Language code for pretrained model

        :param half_precision: Use half precision or not
        """

        # Model initialization
        self.model = torch.hub.load('ultralytics/yolov5',
                                               'custom',
                                               path=path,
                                               _verbose=False,
                                               device='mps')


        self.lang: str = language_code
        self.size                       = DEFAULT_SIZE
        self.model.conf                 = DEFAULT_CONF
        # self.model.dmb = True  # NMS IoU threshold
        self.model.iou                  = DEFAULT_IOU
        self.model.agnostic             = DEFAULT_AGNOSTIC
        self.model.multi_label          = DEFAULT_MULTILABEL
        self.model.max_det              = DEFAULT_MAXDET
        self.model.amp                  = DEFAULT_AMP
        self._USE_HALF_PRECISION        = DEFAULT_HALFPRECISION
        self.model.classes = list(range(0, 41))  # All classes


        self.model.modules()
        self._USE_CUDA: bool = torch.cuda.is_available()

        if self._USE_CUDA:
            self.model.cuda()
        if self._USE_HALF_PRECISION:
            self.model.half()

    def __call__(self, data: Union[str, Any]):
        return self.model(data, self.size)

    def setParams(self, params):
        self.size = params.size
        self.model.conf = params.conf
        self.model.iou = params.iou
        self.model.agnostic = params.agnostic
        self.model.multi_label = params.multi_label
        self.model.max_det = params.max_det
        self.model.amp = params.amp
        self._USE_HALF_PRECISION: bool = params.half_precision
