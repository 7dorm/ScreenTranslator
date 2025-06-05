# Screen Translator

A web-based application to detect, extract, and translate English text from images, with a focus on extensibility and real-time processing.

## Features
- **Text Detection**: Uses YOLOv5 to identify text regions in images.
- **Text Correction**: Corrects misrecognized text (e.g., "th3@pple" → "the apple") using local dictionaries or Datamuse API.
- **Translation**: Translates detected English text to Russian via Google Translate (deep-translator).
- **Web Interface**: Simple Flask-based UI for file uploads and result display.
- **REST API**: Supports media processing with configurable parameters.
- **Extensibility**: Modular architecture for adding new language models or detection modules.
- **Video Processing**: Planned feature to process with bounding boxes and translations.

## Installation

### Prerequisites
- Python 3.9+
- Operating System: Windows 10/11, UNIX-based systems
- GPU (NVIDIA with CUDA 10.2+ recommended for performance)

### From source
1. Clone the repository:
   ```bash
   git clone https://github.com/7dorm/ScreenTranslator.git
   cd ScreenTranslator
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run as a module:
   ```bash
   python -m ScreenTranslator run path/to/input.jpg
   python -m ScreenTranslator server
   ```

### As a package
1. Install locally:
   ```bash
   pip install ScreenTranslator
   ```
2. Use via command-line:
   ```bash
   # Start server
   ScreenTranslator server
    
   # Run translation on a file
   ScreenTranslator run path/to/input.jpg
   ScreenTranslator run path/to/input.jpg path/to/output/folder
   ```

### Dependencies
- torch>=1.8.0
- ultralytics>=8.2.34
- deep-translator
- flask
- pillow>=10.3.0
- numpy>=1.23.5
- opencv-python>=4.1.1
- See `requirements.txt` for full list.

## Usage

### Web Interface
1. Open `http://localhost:5000` in your browser.
2. Upload an image file.
3. View processed results with bounding boxes and translated text.
4. Download results as a ZIP file containing processed media and text.

### REST API
- **Endpoint**: `POST /ScreenTranslatorAPI/process`
- **Parameters**:
  - `File`: Image file (e.g., JPEG, PNG).
  - `Params` (optional JSON):
    ```json
    {
      "size": 1500,
      "conf": 0.2,
      "iou": 0.3,
      "agnostic": true,
      "multi_label": false,
      "max_det": 3000,
      "amp": true,
      "half_precision": true,
      "rough_text_recognition": true
    }
    ```
- **Response**:
  ```json
  {
    "status": "File processed",
    "boxed_url": "/ScreenTranslatorAPI/boxed/<filename>",
    "recognized_text": "Detected text",
    "translated_text": "Translated text",
    "filename": "<filename>"
  }
  ```
- **Example**:
  ```bash
  curl -X POST "http://localhost:5000/ScreenTranslatorAPI/process" \
  -F "File=@image.jpg" \
  -F 'Params={"conf": 0.3}'
  ```

### File Downloads
- Boxed media: `GET /ScreenTranslatorAPI/boxed/<filename>`
- Translated media: `GET /ScreenTranslatorAPI/translated/<filename>`

## Architecture
- **Microservices**:
  - `MPNNModel.py`: YOLOv5-based text detection.
  - `CorrectingWordsByAPI.py` & `CorretingWords.py`: Text correction services.
  - `WordUtils.py`: Merges detected text into words.
- **Plugin-based**:
  - `Medipy.py`: Core plugin manager.
  - `MPDetect.py`: Detection plugin for images.
  - `MPCustom.py`: Custom image processing.
- **Deployment**: Flask server with Nginx, GPU support for performance.

## Development
- **Extensibility**: Add new models via `Medipy.addModel()`.
- **Text Correction**: Uses n-grams and Levenshtein distance for accuracy.
- **Translation**: Context-aware via Google Translate API.

## Limitations
- Video processing is under development.
- Large images may trigger DOS protection (>89MP).
- Translation service availability impacts functionality.

## Contributing
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit changes (`git commit -m "Add feature"`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request.

## Authors
- Dunaev Artemiy Aleksandrovich
- Chebotareva Anna Vladimirovna
- Rebrin Sergey Aleksandrovich
- Lyskov Arseniy Aleksandrovich

## License
MIT License
