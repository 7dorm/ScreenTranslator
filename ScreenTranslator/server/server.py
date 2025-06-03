import os
import sys
import logging
import pathlib
import traceback
from flask import Flask, request, jsonify, send_from_directory, render_template
from flasgger import Swagger, swag_from
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from ScreenTranslator.tools.Medipy import Medipy
from ScreenTranslator.API import *
from ScreenTranslator.constants import *

# Windovod issue
if sys.platform == "win32":
    pathlib.PosixPath = pathlib.WindowsPath

# Flask app setup
app = Flask(__name__)
swagger = Swagger(app)

model = Medipy(show=False)
for model_path in MODEL_PATHS:
    model.addModel(model_path, 'en')

# Rate limiting
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["100000000 per day", "1000 per minute"])

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ScreenTranslatorAPI/boxed/symbols/<filename>", methods=["GET"])
@swag_from("apidocs/get_boxed_symbols.yml")
def get_boxed_symbols(filename):
    path = os.path.join(FOLDER_IMAGE_BOXED_SYMBOLS, filename)
    if not os.path.isfile(path):
        return jsonify({"Error": "File not found"}), 404
    return send_from_directory(FOLDER_IMAGE_BOXED_SYMBOLS, filename)

@app.route("/ScreenTranslatorAPI/boxed/words/<filename>", methods=["GET"])
@swag_from("apidocs/get_boxed_words.yml")
def get_boxed_words(filename):
    path = os.path.join(FOLDER_IMAGE_BOXED_WORDS, filename)
    if not os.path.isfile(path):
        return jsonify({"Error": "File not found"}), 404
    return send_from_directory(FOLDER_IMAGE_BOXED_WORDS, filename)

@app.route("/ScreenTranslatorAPI/translated/rough/<filename>", methods=["GET"])
@swag_from("apidocs/get_translated_rough.yml")
def get_translated_rough(filename):
    path = os.path.join(FOLDER_IMAGE_TRANSLATED_ROUGH, filename)
    if not os.path.isfile(path):
        return jsonify({"Error": "File not found"}), 404
    return send_from_directory(FOLDER_IMAGE_TRANSLATED_ROUGH, filename)

@app.route("/ScreenTranslatorAPI/translated/corrected/<filename>", methods=["GET"])
@swag_from("apidocs/get_translated_corrected.yml")
def get_translated_corrected(filename):
    path = os.path.join(FOLDER_IMAGE_TRANSLATED_CORRECTED, filename)
    if not os.path.isfile(path):
        return jsonify({"Error": "File not found"}), 404
    return send_from_directory(FOLDER_IMAGE_TRANSLATED_CORRECTED, filename)


@app.route("/ScreenTranslatorAPI/process", methods=["POST"])
@limiter.limit("10000 per minute")
@swag_from("apidocs/post_process.yml")
def post_process():
    if 'File' not in request.files or request.files['File'].filename == '':
        return jsonify({'Error': 'No file uploaded'}), 400
    file = request.files['File']

    ext = f'.{file.filename.rsplit(".", 1)[1].lower()}' if '.' in file.filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"Error": "Invalid file type"}), 400
    file.seek(0, os.SEEK_END)
    if file.tell() > MAX_FILE_SIZE:
        return jsonify({"Error": "Invalid file size"}), 400
    file.seek(0)
    

    filepath = os.path.join(FOLDER_UPLOADS, file.filename)
    file.save(filepath)

    params_json = request.form.get('Params')
    try:
        API_request = API_Request(filepath, params_json)
    except Exception as e:
        logger.error(f"Invalid params JSON: {str(e)}")
        return jsonify({"Error": "Invalid params JSON", "Error details": str(e)}), 500

    try:
        API_response = API_Process(API_request, model)
        print(json.dumps(API_response.to_dict(), ensure_ascii=False, indent=4))
        return API_response.jsonify()
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Processing failed: {str(e)}")
        return jsonify({"Error": "Processing failed", "Error details": str(e)}), 500


def start_server():
    reset_temp_folders()
    app.run(debug=True)  # host="0.0.0.0", port=5000
