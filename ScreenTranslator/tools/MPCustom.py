import threading
import time
from queue import Queue
from typing import Union

import cv2
import numpy as np
from PIL import Image
from vidgear.gears import WriteGear

from ScreenTranslator.tools.base import BaseDetection
from ScreenTranslator.constants import FRAME_QUEUE_SIZE
from ScreenTranslator.tools.exceptions import VideoNotInitializedException


class Custom:
    def __init__(self, path, process_function, output_name: str = None, show = False):
        self.path = path
        self.process_function = process_function
        self.output_name = output_name
        self.show = show


class CustomVideo(Custom):
    def __init__(self, path: Union[str, int],
                 process_function,
                 output_name: str = None,
                 show: bool = False) -> None:
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
        print(self.frame)
        _ = self.process_function(self.frame)

        self.prev_time: float = time.time()
        self.frame_count: int = 0

        # Video writer setup
        if self.output_name:
            self.writer: WriteGear = WriteGear(output=self.output_name)
            self.writer_queue: Queue = Queue()
            self.writer_thread: threading.Thread = threading.Thread(target=self.video_writer_worker)
            self.writer_thread.start()


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
                # with open(f"video/{self.output_name}_{self.frame_count}.txt", 'w') as f:
                #     f.write(str(result.xyxyn))

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
                    self.cap.release()
                    if self.output_name:
                        self.writer_thread.join()
                        self.writer_queue.empty()
                        self.writer.close()
                    cv2.destroyAllWindows()
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
    def __init__(self, path: str, process_function, output_name: str = None, show: bool = False) -> None:
        super().__init__(path, process_function, output_name, show)
        self.result: BaseDetection = self.process_function(self.path)  # Directly process image path
        if self.show:
            self.result.frame.show()
        if self.output_name:
            self.result.frame.save(output_name)

    def __call__(self) -> Image:
        return self.result.frame

