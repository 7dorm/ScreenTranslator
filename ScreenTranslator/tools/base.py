import cv2
import pandas
import numpy as np

from PIL import Image
from typing import Union

class BaseDetection:
    def __init__(self,
                 xyxyn: pandas.DataFrame,
                 image_boxed_symbols: Union[Union[cv2.Mat, np.ndarray], Image.Image],
                 image_boxed_words: Union[Union[cv2.Mat, np.ndarray], Image.Image],
                 image_translated_rough: Union[Union[cv2.Mat, np.ndarray], Image.Image],
                 image_translated_corrected: Union[Union[cv2.Mat, np.ndarray], Image.Image],
                 bounding_boxes_symbols: list = [],
                 bounding_boxes_words: list = [],
                 text_rough_recognized: str = "",
                 text_rough_translated: str = "",
                 text_corrected_recognized: str = "",
                 text_corrected_translated: str = "") -> None:
        
        self.xyxyn: pandas.DataFrame = xyxyn
        self.image_boxed_symbols: Union[Union[cv2.Mat, np.ndarray], Image] = image_boxed_symbols
        self.image_boxed_words: Union[Union[cv2.Mat, np.ndarray], Image] = image_boxed_words
        self.image_translated_rough: Union[Union[cv2.Mat, np.ndarray], Image] = image_translated_rough
        self.image_translated_corrected: Union[Union[cv2.Mat, np.ndarray], Image] = image_translated_corrected
        self.bounding_boxes_symbols: list = bounding_boxes_symbols
        self.bounding_boxes_words: list = bounding_boxes_words
        self.text_rough_recognized: str = text_rough_recognized
        self.text_rough_translated: str = text_rough_translated
        self.text_corrected_recognized: str = text_corrected_recognized
        self.text_corrected_translated: str = text_corrected_translated




