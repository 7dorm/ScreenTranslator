import cv2
import pandas
import numpy as np

from PIL import Image
from typing import Union

class BaseDetection:
    def __init__(self,
                 xyxyn: pandas.DataFrame,
                 frame: Union[Union[cv2.Mat, np.ndarray], Image.Image],
                 text: dict = None,
                 translated: dict = None) -> None:
        if text is None:
            text = {}
        self.xyxyn: pandas.DataFrame = xyxyn
        self.frame: Union[Union[cv2.Mat, np.ndarray], Image] = frame
        self.text: dict = text
        self.translated: dict = translated




