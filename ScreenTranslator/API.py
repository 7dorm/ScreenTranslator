from flask import jsonify
from typing import Any
from ScreenTranslator.tools.Medipy import *
from ScreenTranslator.constants import *
import os, zipfile, shutil, json

class API_Response:
    def __init__(
        self,
        json_model_params: str = "",
        image_boxed_characters_url: str = "",
        image_boxed_words_url: str = "",
        image_translated_rough_url: str = "",
        image_translated_corrected_url: str = "",
        json_characters: list[str] = None,
        json_words: list[str] = None,
        text_rough_recognized: list[str] = None,
        text_rough_translated: list[str] = None,
        text_corrected_recognized: list[str] = None,
        text_corrected_translated: list[str] = None
    ):
        self.json_model_params = json_model_params
        self.image_boxed_characters_url = image_boxed_characters_url 
        self.image_boxed_words_url = image_boxed_words_url
        self.image_translated_rough_url = image_translated_rough_url
        self.image_translated_corrected_url = image_translated_corrected_url
        self.json_characters = json_characters if json_characters is not None else [[]]
        self.json_words = json_words if json_words is not None else [[]]
        self.text_rough_recognized = text_rough_recognized if text_rough_recognized is not None else []
        self.text_rough_translated = text_rough_translated if text_rough_translated is not None else []
        self.text_corrected_recognized = text_corrected_recognized if text_corrected_recognized is not None else []
        self.text_corrected_translated = text_corrected_translated if text_corrected_translated is not None else []

    def to_dict(self) -> dict:
        return {
            "Image boxed characters url": self.image_boxed_characters_url,
            "Image boxed words url": self.image_boxed_words_url,
            "Image translated rough url": self.image_translated_rough_url,
            "Image translated corrected url": self.image_translated_corrected_url,
            "JSON model params": self.json_model_params,
            "JSON characters": self.json_characters,
            "JSON words": self.json_words,
            "Text rough recognized": self.text_rough_recognized,
            "Text rough translated": self.text_rough_translated,
            "Text corrected recognized": self.text_corrected_recognized,
            "Text corrected translated": self.text_corrected_translated
        }

    def jsonify(self):
        return jsonify(self.to_dict())
    

class API_Request:
    def __init__(
        self,
        filepath: str,
        params_json: str = None):

        self.filepath = filepath
        
        self.filename = os.path.basename(filepath)
        self.name, self.ext = os.path.splitext(self.filename)
        self.ext = self.ext.lower()

        self.size               = DEFAULT_SIZE
        self.conf               = DEFAULT_CONF
        self.iou                = DEFAULT_IOU
        self.agnostic           = DEFAULT_AGNOSTIC
        self.multi_label        = DEFAULT_MULTILABEL
        self.max_det            = DEFAULT_MAXDET
        self.amp                = DEFAULT_AMP
        self.half_precision     = DEFAULT_HALFPRECISION

        if params_json is not None and params_json.strip():
            self._apply_params(params_json)

    def _apply_params(self, params_json: str):
        try:
            params = json.loads(params_json)
            if not isinstance(params, dict):
                raise ValueError("Params must be a JSON object")
            if 'size' in params:
                self.size = self._validate_int(params['size'], SIZE_MIN, SIZE_MAX)
            if 'conf' in params:
                self.conf = self._validate_float(params['conf'], CONF_MIN, CONF_MAX)
            if 'iou' in params:
                self.iou = self._validate_float(params['iou'], IOU_MIN, IOU_MAX)
            if 'agnostic' in params:
                self.agnostic = self._validate_bool(params['agnostic'])
            if 'multi_label' in params:
                self.multi_label = self._validate_bool(params['multi_label'])
            if 'max_det' in params:
                self.max_det = self._validate_int(params['max_det'], MAXDET_MIN, MAXDET_MAX)
            if 'amp' in params:
                self.amp = self._validate_bool(params['amp'])
            if 'half_precision' in params:
                self.half_precision = self._validate_bool(params['half_precision'])
                
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
    

def API_Process(request: API_Request, model: Medipy = None) -> API_Response:
    for folder in TEMP_FOLDERS:
        os.makedirs(folder, exist_ok=True)
    if not request.filepath == os.path.join(FOLDER_UPLOADS, request.filename):
        shutil.copy(request.filepath, os.path.join(FOLDER_UPLOADS, request.filename))
        request.filepath = os.path.join(FOLDER_UPLOADS, request.filename)

    if model is None:
        model = Medipy()
        for model_path in MODEL_PATHS:
            model.addModel(model_path, 'en')
    model.setParams(request)
    result = model.process(request.filepath)

    response = API_Response()
    if isinstance(result, CustomImage):
        image_boxed_characters = result.result.image_boxed_characters
        if image_boxed_characters.mode == 'RGBA':
            image_boxed_characters = image_boxed_characters.convert('RGB')
        image_boxed_characters.save(os.path.join(FOLDER_IMAGE_BOXED_CHARACTERS, request.filename))

        image_boxed_words = result.result.image_boxed_words
        if image_boxed_words.mode == 'RGBA':
            image_boxed_words = image_boxed_words.convert('RGB')
        image_boxed_words.save(os.path.join(FOLDER_IMAGE_BOXED_WORDS, request.filename))

        image_translated_rough = result.result.image_translated_rough
        if image_translated_rough.mode == 'RGBA':
            image_translated_rough = image_translated_rough.convert('RGB')
        image_translated_rough.save(os.path.join(FOLDER_IMAGE_TRANSLATED_ROUGH, request.filename))

        image_translated_corrected = result.result.image_translated_corrected
        if image_translated_corrected.mode == 'RGBA':
            image_translated_corrected = image_translated_corrected.convert('RGB')
        image_translated_corrected.save(os.path.join(FOLDER_IMAGE_TRANSLATED_CORRECTED, request.filename))

        with open(os.path.join(FOLDER_LABELS_CHARACTERS, f"{request.name}.json"), "w", encoding="utf-8") as f:
            f.write(str(result.result.json_characters))

        with open(os.path.join(FOLDER_LABELS_WORDS, f"{request.name}.json"), "w", encoding="utf-8") as f:
            f.write(str(result.result.json_words))


        response.image_boxed_characters_url = f"/ScreenTranslatorAPI/boxed/characters/{request.filename}"
        response.image_boxed_words_url = f"/ScreenTranslatorAPI/boxed/words/{request.filename}"
        response.image_translated_rough_url = f"/ScreenTranslatorAPI/translated/rough/{request.filename}"
        response.image_translated_corrected_url = f"/ScreenTranslatorAPI/translated/corrected/{request.filename}"
        response.json_characters = str(result.result.json_characters)
        response.json_words = str(result.result.json_words)
        response.text_rough_recognized = str(result.result.text_rough_recognized)
        response.text_rough_translated = str(result.result.text_rough_translated)
        response.text_corrected_recognized = str(result.result.text_corrected_recognized)
        response.text_corrected_translated = str(result.result.text_corrected_translated)
    elif isinstance(result, CustomVideo):
        raise ValueError("Video processing not yet implemented")
    else:
        raise ValueError("Invalid result type from Medipy")

    
    return response


def reset_temp_folders():
    for folder in TEMP_FOLDERS:
        os.makedirs(folder, exist_ok=True)
    shutil.rmtree(FOLDER_PROCESSED)
    shutil.rmtree(FOLDER_UPLOADS)
    for folder in TEMP_FOLDERS:
        os.makedirs(folder, exist_ok=True)
        

def runScreenTranslator(filePath: str, destinationPath: str = None, request: API_Request = None):
    if destinationPath is None:
        destinationPath = os.path.dirname(filePath)
    if request is None:
        request = API_Request(filePath)

    response = API_Process(request)
    filename, name, ext = request.filename, request.name, request.ext
    zip_name = os.path.join(destinationPath, f"ScreenTranslator_{name}.zip")

    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(os.path.join(FOLDER_IMAGE_TRANSLATED_CORRECTED, filename), f"{name}_image_translated_corrected{ext}")
        zipf.write(os.path.join(FOLDER_IMAGE_TRANSLATED_ROUGH, filename), f"{name}_image_translated_rough{ext}")
        zipf.write(os.path.join(FOLDER_IMAGE_BOXED_WORDS, filename), f"{name}_image_boxed_words{ext}")
        zipf.write(os.path.join(FOLDER_IMAGE_BOXED_CHARACTERS, filename), f"{name}_image_boxed_characters{ext}")
        zipf.write(os.path.join(FOLDER_LABELS_WORDS, f"{name}.json"), f"{name}_json_words.json")
        zipf.write(os.path.join(FOLDER_LABELS_CHARACTERS, f"{name}.json"), f"{name}_json_characters.json")
        zipf.writestr(f"{name}_text_corrected_recognized.txt", response.text_corrected_recognized)
        zipf.writestr(f"{name}_text_corrected_translated.txt", response.text_corrected_translated)
        zipf.writestr(f"{name}_text_rough_recognized.txt", response.text_rough_recognized)
        zipf.writestr(f"{name}_text_rough_translated.txt", response.text_rough_translated)