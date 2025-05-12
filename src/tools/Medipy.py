from typing import List, Union

from tools.MPCustom import CustomImage, CustomVideo
from tools.MPDetect import Detection
from tools.MPNNModel import NNModel


class Medipy:
    def __init__(self, show: bool = False, params = None) -> None:
        self.models: List[NNModel] = []
        self.detector: Detection = Detection(self.models)
        self.show: bool = show
        self.params = params

    def addModel(self, path: str, language_code: str) -> None:
        self.models.append(NNModel(path, language_code, self.params))
        self.detector = Detection(self.models)

    def process(self, filepath: str, output_name: str = None, size = None) ->  Union[CustomImage, CustomVideo, None]:
        return self.detector(filepath, output_name, self.show)


if __name__ == "__main__":
    obj = Medipy(show=False)
    obj.addModel('best.pt', 'en')
    # image: CustomImage = obj.process("/Users/deu/Downloads/1.webp")
    # print(image.result.text.keys())
    # image: CustomImage = obj.process("/Users/deu/Downloads/test2.jpg")
    # image: CustomImage = obj.process("/Users/deu/Downloads/test3.jpg")
    image: CustomImage = obj.process("/Users/deu/large_image.bmp")
    # image: CustomImage = obj.process("/Users/deu/Downloads/test5.jpg")
    # image: CustomImage = obj.process("/Users/deu/Downloads/test6.jpg")
    # image: CustomImage = obj.process("/Users/deu/Downloads/test7.jpg")



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