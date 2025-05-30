from flask import jsonify
from typing import Any
import os, json

class API_Response:
    def __init__(
        self,
        boxed_url: str = "",
        translated_url: str = "",
        recognized_text: list[str] = None,
        translated_text: list[str] = None,
    ):
        self.boxed_url = boxed_url
        self.translated_url = translated_url
        self.recognized_text = recognized_text if recognized_text is not None else []
        self.translated_text = translated_text if translated_text is not None else []

    def to_dict(self, ) -> dict:
        # if rough_text_recognition:
        #     return {"Recognized text": self.recognized_text[0]}
        return {
            "Boxed url": self.boxed_url,
            "Translated url": self.translated_url,
            "Recognized text": self.recognized_text,
            "Translated text": self.translated_text,
        }

    def jsonify(self):
        return jsonify(self.to_dict())
    

class API_Request:
    def __init__(
        self,
        filepath: str,
        params_json: str):

        self.rough_text_recognition = False
        self.filepath = filepath
        
        filename = os.path.basename(filepath)
        self.name, self.ext = os.path.splitext(filename)
        self.ext = self.ext.lower()

        self.size = 1500
        self.conf = 0.2
        self.iou = 0.3
        self.agnostic = True
        self.multi_label = False
        self.max_det = 3000
        self.amp = True
        self.half_precision = True

        if params_json:
            self._apply_params(params_json)

    def _apply_params(self, params_json: str):
        try:
            params = json.loads(params_json)
            if not isinstance(params, dict):
                raise ValueError("Params must be a JSON object")
            if 'size' in params:
                self.size = self._validate_int(params['size'], 640, 4096)
            if 'conf' in params:
                self.conf = self._validate_float(params['conf'], 0.1, 0.9)
            if 'iou' in params:
                self.iou = self._validate_float(params['iou'], 0.1, 0.9)
            if 'agnostic' in params:
                self.agnostic = self._validate_bool(params['agnostic'])
            if 'multi_label' in params:
                self.multi_label = self._validate_bool(params['multi_label'])
            if 'max_det' in params:
                self.max_det = self._validate_int(params['max_det'], 1, 10000)
            if 'amp' in params:
                self.amp = self._validate_bool(params['amp'])
            if 'half_precision' in params:
                self.half_precision = self._validate_bool(params['half_precision'])
            if 'rough_text_recognition' in params:
                self.rough_text_recognition = self._validate_bool(params['rough_text_recognition'])
                
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in Params: {str(e)}")

    @staticmethod
    def _validate_int(value: Any, min_val: int, max_val: int) -> int:
        try:
            num = int(value)
        except (TypeError, ValueError):
            raise ValueError(f"Must be integer, got {type(value).__name__}")
        
        if not (min_val <= num <= max_val):
            raise ValueError(f"Must be between {min_val} and {max_val}, got {num}")
        return num

    @staticmethod
    def _validate_float(value: Any, min_val: float, max_val: float) -> float:
        try:
            num = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"Must be number, got {type(value).__name__}")
        
        if not (min_val <= num <= max_val):
            raise ValueError(f"Must be between {min_val} and {max_val}, got {num}")
        return num

    @staticmethod
    def _validate_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        raise ValueError(f"Must be boolean, got {type(value).__name__}")
    