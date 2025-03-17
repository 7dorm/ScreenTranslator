import cv2
import pandas
import numpy as np

from PIL import Image
from typing import Union

class BaseDetection:
    def __init__(self, xyxyn: pandas.DataFrame, frame: Union[Union[cv2.Mat, np.ndarray], Image.Image]) -> None:
        self.xyxyn: pandas.DataFrame = xyxyn
        self.frame: Union[Union[cv2.Mat, np.ndarray], Image] = frame




