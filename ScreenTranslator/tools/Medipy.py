from typing import List, Union

from ScreenTranslator.tools.MPCustom import CustomImage, CustomVideo
from ScreenTranslator.tools.MPDetect import Detection
from ScreenTranslator.tools.MPNNModel import NNModel


class Medipy:
    def __init__(self, show: bool = False, params = None) -> None:
        self.models: List[NNModel] = []
        self.detector: Detection = Detection(self.models)
        self.show: bool = show
        self.params = params

    def addModel(self, path: str, language_code: str) -> None:
        self.models.append(NNModel(path, language_code, self.params))
        self.detector = Detection(self.models)

    def setParams(self, params):
        for i in range(len(self.models)):
            self.models[i].setParams(params)
        self.detector = Detection(self.models)

    def process(self, filepath: str, output_name: str = None, size = None) ->  Union[CustomImage, CustomVideo, None]:
        return self.detector(filepath, output_name, self.show)