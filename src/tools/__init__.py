import time
import torch
import threading

from PIL import Image
from queue import Queue

from objc.simd import vector_uint2

from constants import *
from src.tools.base import *
from typing import List, Union, Any
from vidgear.gears import WriteGear
from mutils import ImageUtils, WordUtils
from models.common import AutoShape, Detections
from src.tools.exceptions import IncorrectFileTypeException, VideoNotInitializedException

class Logger:
    pass


class CustomVideo(Custom):
    def __init__(self, path: Union[str, int],
                 process_function,
                 output_name: str = None,
                 show: bool = True) -> None:
        super().__init__(path, process_function, output_name, show)

        self.cap: cv2.VideoCapture = cv2.VideoCapture(self.path)
        self.loaded: bool = True

        if not self.cap.isOpened():
            self.loaded = False
            return

        # Get video properties from first frame
        self.success, self.frame = self.cap.read()
        if not self.success:
            self.loaded = False
            return

        # Warmup model
        _ = self.process_function(self.frame)

        # Video writer setup
        if self.output_name:
            self.writer: WriteGear = WriteGear(output=self.output_name)
            self.writer_queue: Queue = Queue()
            self.writer_thread: threading.Thread = threading.Thread(target=self.video_writer_worker)
            self.writer_thread.start()
            self.prev_time: float = time.time()
            self.frame_count: int = 0

    def __iter__(self):
        return self

    def __next__(self) -> BaseDetection:
        if not self.loaded:
            raise VideoNotInitializedException()

        if self.success:
            # Process frame
            result: BaseDetection = self.process_function(self.frame)

            output_frame: Union[cv2.Mat, np.ndarray] = result.frame

            # Calculate FPS
            self.frame_count += 1

            if self.output_name:
                with open(f"video/{self.output_name}_{self.frame_count}.txt", 'w') as f:
                    f.write(str(result.xyxyn))

                # Write to queue
                if self.writer_queue.qsize() < FRAME_QUEUE_SIZE:
                    self.writer_queue.put(output_frame)

            if self.show:
                curr_time: float = time.time()

                fps: float = self.frame_count / (curr_time - self.prev_time)

                cv2.putText(output_frame,
                            f'FPS: {fps:.1f}',
                            (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 255, 0),
                            2)

                cv2.imshow('Detection', output_frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    raise StopIteration

            self.success, self.frame = self.cap.read()

            return result
        else:
            # Cleanup
            self.cap.release()
            if self.output_name:
                self.writer_thread.join()
                self.writer_queue.put(None)
            cv2.destroyAllWindows()
            raise StopIteration

    def is_loaded(self) -> bool:
        return self.loaded

    def video_writer_worker(self):
        """Dedicated thread for writing video frames."""
        while True:
            frame: Union[cv2.Mat, np.ndarray] = self.writer_queue.get()
            if frame is None:  # Stop signal
                break
            self.writer.write(frame)
        self.writer.close()


class CustomImage(Custom):
    def __init__(self, path: str, process_function, output_name: str = None, show: bool = True) -> None:
        super().__init__(path, process_function, output_name, show)
        self.result: BaseDetection = self.process_function(self.path)  # Directly process image path
        if self.show:
            self.result.frame.show()
        if self.output_name:
            self.result.frame.save(self.output_name)

    def __call__(self) -> Image:
        return self.result.frame


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
        self.model.conf = 0.25  # Confidence threshold
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


class Detection:
    def __init__(self, models: List[NNModel]) -> None:
        self.models: List[NNModel] = models

    def __call__(self, path_to_media: str,
                 output_name: str = None,
                 show: bool = True) -> Union[CustomImage, CustomVideo, None]:
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
        result: Detections = self.select_model(frame)

        if result.xyxyn.index.stop:
            return BaseDetection(
                result.pandas().xyxyn[0],
                ImageUtils.convert_pil_to_cv(
                    ImageUtils.draw_bounding_boxes(
                        ImageUtils.convert_to_pil_image(frame),
                        WordUtils.merger(result.pandas().xyxyn[0])
                    )
                )
            )
        else:
            return BaseDetection(
                result.pandas().xyxyn[0],
                np.squeeze(result.render())
            )

    def process_image(self, path: str) -> BaseDetection:
        result: Detections = self.select_model(path)
        bboxes: dict = WordUtils.merger(result.pandas().xyxyn[0])
        return BaseDetection(
            result.pandas().xyxyn[0],
            ImageUtils.draw_bounding_boxes(Image.open(path), bboxes)
        )

    def select_model(self, frame: Union[Union[cv2.Mat, np.ndarray], str]) -> Union[Detections, None]:
        result: Detections = None
        conf: int = 0

        for model in self.models:
            curr_result: Detections = model(frame)
            curr_conf: int = curr_result.xyxy[0][:, 4].mean()
            if curr_conf > conf:
                conf = curr_conf
                result = curr_result

        return result


class Medipy:
    def __init__(self, show: bool = True) -> None:
        self.models: List[NNModel] = []
        self.detector: Detection = Detection(self.models)
        self.show: bool = show

    def addModel(self, path: str, language_code: str, half_precision: bool = False) -> None:
        self.models.append(NNModel(path, language_code, half_precision))
        self.detector = Detection(self.models)

    def process(self, filepath: str, output_name: str = None) ->  Union[CustomImage, CustomVideo, None]:
        return self.detector(filepath, output_name, self.show)


if __name__ == "__main__":
    obj = Medipy(show=True)
    obj.addModel('best.pt', 'en')
    vid: CustomVideo = obj.process('/Users/deu/Downloads/test.mp4')
    if vid.is_loaded():
        for frame in vid:
            pass


#
#                       TODO: Modify this to Custom Video
#
# import mss
# import mss.tools
# def run_detection_screen(model):
#     """Screen capture detection (cross-platform)."""
#     writer = WriteGear(output='output_video_of_screen.mp4')
#     writer_queue = Queue()
#     writer_thread = threading.Thread(target=video_writer_worker, args=(writer, writer_queue))
#     writer_thread.start()
#     with mss.mss() as sct:
#         monitor = sct.monitors[1]  # Primary monitor
#         print("Screen capture running. Press 'q' to quit.")
#
#         prev_time = time.time()
#         frame_count = 0
#
#         while True:
#             # Capture screen
#             screenshot = sct.grab(monitor)
#             frame = np.array(screenshot)
#             frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
#
#             # Process frame
#             results = process_frame(model, frame)
#             with open(f"screen/video_dataframe_{frame_count}.txt", 'w') as f:
#                 f.write(str(results.pandas().xyxyn[0]))
#             if results.pandas().xyxyn[0].index.stop:
#                 output_frame = convert_pil_to_cv(
#                     draw_bounding_boxes(
#                         convert_to_pil_image(frame),
#                         merger(results.pandas().xyxyn[0])
#                     )
#                 )
#             else:
#                 output_frame = np.squeeze(results.render())
#             # Calculate FPS
#             frame_count += 1
#             curr_time = time.time()
#             fps = frame_count / (curr_time - prev_time)
#             cv2.putText(output_frame, f'FPS: {fps:.1f}', (10, 30),
#                         cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
#
#             if writer_queue.qsize() < FRAME_QUEUE_SIZE:
#                 writer_queue.put(output_frame)
#
#             cv2.imshow('Screen Detection', output_frame)
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
#
#         cv2.destroyAllWindows()