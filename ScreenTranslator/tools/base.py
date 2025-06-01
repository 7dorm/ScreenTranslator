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
                 labels_symbols: dict = {},
                 labels_words: dict = {},
                 text_rough_recognized: dict = {},
                 text_rough_translated: dict = {},
                 text_corrected_recognized: dict = {},
                 text_corrected_translated: dict = {}) -> None:
        
        self.xyxyn: pandas.DataFrame = xyxyn
        self.image_boxed_symbols: Union[Union[cv2.Mat, np.ndarray], Image] = image_boxed_symbols
        self.image_boxed_words: Union[Union[cv2.Mat, np.ndarray], Image] = image_boxed_words
        self.image_translated_rough: Union[Union[cv2.Mat, np.ndarray], Image] = image_translated_rough
        self.image_translated_corrected: Union[Union[cv2.Mat, np.ndarray], Image] = image_translated_corrected
        self.labels_symbols: dict = labels_symbols
        self.labels_words: dict = labels_words
        self.text_rough_recognized: dict = text_rough_recognized
        self.text_rough_translated: dict = text_rough_translated
        self.text_corrected_recognized: dict = text_corrected_recognized
        self.text_corrected_translated: dict = text_corrected_translated




