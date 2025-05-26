from typing import List, Union

import cv2
import numpy as np
from PIL import Image

from tools.MPNNModel import NNModel
from tools.MPCustom import CustomVideo, CustomImage
from tools.base import BaseDetection
from tools.constants import IMAGE_TYPES, VIDEO_TYPES
from tools.exceptions import IncorrectFileTypeException
from tools.mutils import ImageUtils, WordUtils
from tools.mutils import translated_text_on_image
from tools.mutils.ImageUtils import convert_pil_to_cv, resize_image


class Detection:
    def __init__(self, models: List[NNModel]) -> None:
        self.models: List[NNModel] = models

    def __call__(self, path_to_media: str,
                 output_name: str = None,
                 translated: bool = True,
                 only_text: bool = False,
                 show: bool = False) -> Union[CustomImage, CustomVideo, None]:
        """
        Method to process media files
        :param path_to_media: Path to media for processing
        :return: Detected Data

        Supported types:
            For image:
                bmp, dib, jpeg, jpg, jpe, jp2, png, pbm, pgm, ppm, sr, ras, tiff, tif, webp
            For video:
                avi, mp4, mov, mkv, flv, wmv, mpeg, mpg, mpe, m4v, 3gp, 3g2, asf, divx, f4v, m2ts, m2v, m4p, mts, ogm, ogv, qt, rm, vob, webm, xvid
        """

        self.translated = translated
        self.only_text = only_text
        if path_to_media == 0:
            return CustomVideo(0, self.process_frame, output_name, show)

        for image_type in IMAGE_TYPES:
            if image_type in path_to_media:
                return CustomImage(path_to_media, self.process_image, output_name, show)
        else:
            for video_type in VIDEO_TYPES:
                if video_type in path_to_media:
                    return CustomVideo(path_to_media, self.process_frame, output_name, show)
            else:
                raise IncorrectFileTypeException(path_to_media.split('.')[-1])

    def process_frame(self, frame: Union[cv2.Mat, np.ndarray]) -> BaseDetection:
        result, t_model = self.select_model(frame)

        if result.xyxyn[0].size().numel():
            merge, translation = WordUtils.merger(result.pandas().xyxyn[0], True)
            return BaseDetection(
                result.pandas().xyxyn[0],
                ImageUtils.convert_pil_to_cv(
                    ImageUtils.draw_bounding_boxes(
                        ImageUtils.convert_to_pil_image(frame),
                        translation
                    )
                ),
                merge,
                translation
            )
        else:
            return BaseDetection(
                result.pandas().xyxyn[0],
                np.squeeze(result.render())
            )

    def process_image(self, path: str) -> BaseDetection:
        result, t_model = self.select_model(path)
        data = result.pandas().xyxyn[0]
        if data.size:
            bboxes, translated = WordUtils.merger(data, True)

            if t_model.rough:
                letters = list(data['name'])
                letter_params = {
                    letters[i]: {
                        'x_min': float(data['xmin'][i]),
                        'y_min': float(data['ymin'][i]),
                        'x_max': float(data['xmax'][i]),
                        'y_max': float(data['ymax'][i])
                    } for i in range(len(letters))
                }
                letterr = {
                    i: {
                    letters[i]: {
                        'x_min': float(data['xmin'][i]),
                        'y_min': float(data['ymin'][i]),
                        'x_max': float(data['xmax'][i]),
                        'y_max': float(data['ymax'][i])
                    } } for i in range(len(letters))
                }

                return BaseDetection(
                    data,
                    ImageUtils.draw_bounding_boxes(Image.open(path), letter_params),
                    letterr,
                    {}
                )
            return BaseDetection(
                data,
                translated_text_on_image.process_image(Image.open(path), translated, bboxes),
                bboxes,
                translated
            )
        else:
            return BaseDetection(
                data,
                Image.open(path),
                {},
                {}
            )

    def select_model(self, frame: Union[Union[cv2.Mat, np.ndarray], str]):
        result: Detections = None
        conf: int = 0
        best_model = None

        for model in self.models:
            curr_result: Detections = model(frame)
            curr_conf: int = curr_result.xyxy[0][:, 4].mean()
            if result == None or curr_conf > conf:
                conf = curr_conf
                result = curr_result
                best_model = model

        return [result, best_model]
