import os
import sys
import uuid
import json
import logging
import pathlib
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory, render_template
from flasgger import Swagger, swag_from
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from tools.MPCustom import CustomImage, CustomVideo
from tools.Medipy import Medipy
from server.API import API_Request, API_Response
from PIL import Image, ImageOps
import pillow_heif

# Windovod issue
if sys.platform == "win32":
    pathlib.PosixPath = pathlib.WindowsPath

# Flask app setup
app = Flask(__name__)
swagger = Swagger(app)

model = Medipy(show=False)
# model.addModel('tools/cars.pt', 'en')
model.addModel('src/tools/best.pt', 'en')

# Rate limiting
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["100000000 per day", "1000 per minute"])

# Directory setup
BASE_DIR = app.root_path
FOLDER_UPLOADS = os.path.join(BASE_DIR, "static", "Uploads")
FOLDER_PROCESSED = os.path.join(BASE_DIR, "static", "processed")
FOLDER_BOXED = os.path.join(FOLDER_PROCESSED, "boxed")
FOLDER_TRANSLATED = os.path.join(FOLDER_PROCESSED, "translated")
FOLDER_LABELS = os.path.join(FOLDER_PROCESSED, "labels")

# Ensure directories exist
for folder in [FOLDER_UPLOADS, FOLDER_BOXED, FOLDER_TRANSLATED, FOLDER_LABELS]:
    os.makedirs(folder, exist_ok=True)

# File extensions
ALLOWED_EXTENSIONS = {
    'bmp', 'dib', 'jpeg', 'jpg', 'jpe', 'jp2', 'png', 'pbm', 'pgm', 'ppm', 'sr', 'ras', 'tiff', 'tif', 'webp',
    'avi', 'mp4', 'mov', 'mkv', 'flv', 'wmv', 'mpeg', 'mpg', 'mpe', 'm4v', '3gp', '3g2', 'asf', 'divx', 'f4v',
    'm2ts', 'm2v', 'm4p', 'mts', 'ogm', 'ogv', 'qt', 'rm', 'vob', 'webm', 'xvid'
}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 10MB

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Medipy model setup

def clean_old_files(directory, max_age_hours=24):
    """Remove files older than max_age_hours from directory."""
    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) and datetime.fromtimestamp(os.path.getmtime(file_path)) < cutoff:
                os.unlink(file_path)
                logger.info(f"Deleted old file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete {file_path}: {e}")

def parse_yolo_labels(file_path):
    """Parse YOLO labels into text."""
    names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
             'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', ',', '?', '!', '@']
    entries = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) < 2:
                    continue
                class_id = int(float(parts[0]))
                x_center = float(parts[1])
                entries.append((x_center, class_id))
        entries.sort(key=lambda x: x[0])
        return ''.join(names[class_id] for _, class_id in entries)
    except Exception as e:
        logger.error(f"Failed to parse YOLO labels: {e}")
        return ""

@app.route("/")
def index():
    """Render the main page."""
    return render_template("index.html")

@app.route("/ScreenTranslatorAPI/boxed/<filename>")
@swag_from("apidocs/downloadBoxed.yml")
def download_boxed(filename):
    """Serve boxed image/video file."""
    # filename = secure_filename(filename)
    file_path = os.path.join(FOLDER_BOXED, filename)
    try:
        if not os.path.isfile(file_path):
            logger.error(f"File not found: {file_path}")
            return jsonify({"error": "File not found"}), 404
        if not os.access(file_path, os.R_OK):
            logger.error(f"File not readable: {file_path}")
            return jsonify({"error": "File access forbidden"}), 403
        logger.info(f"Serving file: {file_path}")
        return send_from_directory(FOLDER_BOXED, filename)
    except Exception as e:
        logger.error(f"Error serving file {file_path}: {e}")
        return jsonify({"error": "Server error", "details": str(e)}), 500

@app.route("/ScreenTranslatorAPI/translated/<filename>")
@swag_from("apidocs/downloadTranslated.yml")
def download_translated(filename):
    """Serve translated file."""
    # filename = secure_filename(filename)
    file_path = os.path.join(FOLDER_TRANSLATED, filename)
    try:
        if not os.path.isfile(file_path):
            logger.error(f"File not found: {file_path}")
            return jsonify({"error": "File not found"}), 404
        if not os.access(file_path, os.R_OK):
            logger.error(f"File not readable: {file_path}")
            return jsonify({"error": "File access forbidden"}), 403
        logger.info(f"Serving file: {file_path}")
        return send_from_directory(FOLDER_TRANSLATED, filename)
    except Exception as e:
        logger.error(f"Error serving file {file_path}: {e}")
        return jsonify({"error": "Server error", "details": str(e)}), 500

def validate_file(file):
    """Validate uploaded file type and size."""
    if not file or not file.filename:
        return False
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    # Allow any image type supported by Pillow
    file.seek(0, os.SEEK_END)
    if file.tell() > MAX_FILE_SIZE:
        return False
    file.seek(0)
    return True

@app.route("/ScreenTranslatorAPI/process", methods=["POST"])
@limiter.limit("10000 per minute")
@swag_from("apidocs/fileProcess.yml")
def process_file():
    """Process uploaded image or video synchronously."""
    if 'File' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['File']
    if not validate_file(file):
        return jsonify({"error": "Invalid file type or size"}), 400

    # Generate unique filename
    filename = f"{uuid.uuid4()}.jpg"  # Force .jpg extension
    filepath = os.path.join(FOLDER_UPLOADS, filename)

    # Convert image to JPEG
    try:
        pillow_heif.register_heif_opener()  # Enable HEIC support
        img = Image.open(file)
        # Reset orientation based on EXIF data
        img = ImageOps.exif_transpose(img)  # Corrects rotation
        if img.mode == 'RGBA':
            img = img.convert('RGB')  # Convert RGBA to RGB for JPEG
        img.save(filepath, 'JPEG', quality=95)
        logger.info(f"Converted and saved file: {filepath}")
    except Exception as e:
        logger.error(f"Image conversion failed: {e}")
        return jsonify({"error": "Image conversion failed", "details": str(e)}), 400

    # Process parameters
    params_json = request.form.get('Params', '{}')
    try:
        params = json.loads(params_json)
    except json.JSONDecodeError:
        os.remove(filepath)
        return jsonify({"error": "Invalid Params JSON"}), 400

    # Process with Medipy
    API_request = API_Request(filepath, params_json)
    API_response = API_Response()
    try:
        output_path = f"{FOLDER_BOXED}/{filename}"
        result = compute(API_request)
        if isinstance(result, CustomImage):
            image = result.result.frame
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            image.save(output_path, 'JPEG', quality=95)
            API_response.boxed_url = f"/translator/ScreenTranslatorAPI/boxed/{filename}"
            API_response.recognized_text = str(result.result.text)
            API_response.translated_text = str(result.result.translated)
        elif isinstance(result, CustomVideo):
            API_response.boxed_url = f"/translator/ScreenTranslatorAPI/boxed/{filename}"
            API_response.recognized_text = "Video processing complete"
        else:
            raise ValueError("Invalid result type from Medipy")

        if not os.path.isfile(output_path):
            raise RuntimeError(f"Output file not saved: {output_path}")
        if not os.access(output_path, os.R_OK):
            raise RuntimeError(f"Output file not readable: {output_path}")
        logger.info(f"Saved processed file: {output_path}")

        with open(os.path.join(FOLDER_PROCESSED, f"{filename}.json"), 'w') as f:
            json.dump(API_response.to_dict(), f)

        logger.info(f"Processed file: {filename}")
        os.remove(filepath)
        return jsonify({
            "status": "File processed",
            "boxed_url": API_response.boxed_url,
            "recognized_text": API_response.recognized_text,
            "translated_text": API_response.translated_text,
            "filename": filename
        }), 200
    except Exception as e:
        logger.error(f"Processing failed for {filename}: {e}")
        os.remove(filepath)
        return jsonify({"error": "Processing failed", "details": str(e)}), 500

def compute(API_request):
    model.setParams(API_request)
    return model.process(API_request.filepath)

def start_server():
    for folder in [FOLDER_UPLOADS, FOLDER_PROCESSED, FOLDER_BOXED, FOLDER_TRANSLATED, FOLDER_LABELS]:
        os.makedirs(folder, exist_ok=True)
        clean_old_files(folder)
        os.makedirs(folder, exist_ok=True)

    # Run with WSGI in production
    app.run(debug=True)  # host="0.0.0.0", port=5000
