import cv2
import pandas
import numpy as np

from PIL import Image
from typing import Union

class BaseDetection:
    def __init__(self, xyxyn: pandas.DataFrame, frame: Union[Union[cv2.Mat, np.ndarray], Image.Image]) -> None:
        self.xyxyn: pandas.DataFrame = xyxyn
        self.frame: Union[Union[cv2.Mat, np.ndarray], Image] = frame


class Custom:
    def __init__(self, path, process_function, output_name: str = None, show = True):
        self.path = path
        self.process_function = process_function
        self.output_name = output_name
        self.show = show

