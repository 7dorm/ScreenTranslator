from flask import Flask, request, render_template, jsonify, send_from_directory
from flasgger import Swagger, swag_from
from API import API_Request, API_Response
import os
import shutil
import subprocess

app = Flask(__name__)
swagger = Swagger(app)

FOLDER_UPLOADS = os.path.join(app.root_path, "static", "uploads")
FOLDER_PROCESSED = os.path.join(app.root_path, "static", "processed")
FOLDER_BOXED = os.path.join(FOLDER_PROCESSED, "boxed")
FOLDER_TRANSLATED = os.path.join(FOLDER_PROCESSED, "translated")
FOLDER_LABELS = os.path.join(FOLDER_PROCESSED, "labels")
CLEAN_UP_FILES = True


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ScreenTranslatorAPI/boxed/<filename>")
@swag_from("apidocs/downloadBoxed.yml")
def downloadBoxed(filename):
    path = os.path.join(FOLDER_BOXED, filename)
    if not os.path.isfile(path):
        return jsonify({"Error": "File not found"}), 404
    return send_from_directory(FOLDER_BOXED, filename)


@app.route("/ScreenTranslatorAPI/translated/<filename>")
@swag_from("apidocs/downloadTranslated.yml")
def downloadTranslated(filename):
    path = os.path.join(FOLDER_TRANSLATED, filename)
    if not os.path.isfile(path):
        return jsonify({"Error": "File not found"}), 404    
    return send_from_directory(FOLDER_TRANSLATED, filename)


@app.route("/ScreenTranslatorAPI/fileProcess", methods=["POST"])
@swag_from("apidocs/fileProcess.yml")
def fileProcess(rough_text_recognition: bool = False):
    if 'File' not in request.files or request.files['File'].filename == '':
        return jsonify({'Error': 'No file uploaded'}), 400

    file = request.files['File']
    filepath = os.path.join(FOLDER_UPLOADS, file.filename)
    file.save(filepath)

    params_json = request.form.get('Params')
    API_request = API_Request(rough_text_recognition, filepath, params_json)
    API_response = API_Response()

    try:
        run_yolo(API_request, API_response)
        return API_response.jsonify(API_request.rough_text_recognition)

    except Exception as e:
        return jsonify({'Error': 'Processing failed', 'Error details': str(e)}), 500


@app.route("/ScreenTranslatorAPI/imageDetect", methods=["POST"])
@swag_from("apidocs/imageDetect.yml")
def imageDetect():
    return fileProcess(rough_text_recognition=True)


def run_yolo(API_request: API_Request, API_response: API_Response):
    if (API_request.rough_text_recognition):
        command = [
            "python", "yolo/detect.py",
            "--weights", "yolo/best.pt",
            "--source", API_request.filepath,
            "--line-thickness", "1",
            "--img", str(API_request.size),
            "--exist-ok",
            "--save-txt",
            "--save-conf",
            "--name", FOLDER_BOXED,
            "--project", "."
        ]
        subprocess.run(command, check=True)
        
        src_labels = os.path.join(FOLDER_BOXED, "labels")
        if os.path.exists(src_labels):
            for filename in os.listdir(src_labels):
                if filename.endswith(".txt"):
                    src = os.path.join(src_labels, filename)
                    dst = os.path.join(FOLDER_LABELS, filename)
                    os.rename(src, dst)
            os.rmdir(src_labels)

        API_response.recognized_text.append(parse_yolo_labels(
            os.path.join(FOLDER_LABELS, f"{API_request.name}.txt")))
        
    else:
        # For testing
        API_request.rough_text_recognition = True
        API_response.boxed_url = f"/ScreenTranslatorAPI/boxed/{API_request.name}{API_request.ext}"
        run_yolo(API_request, API_response)

def parse_yolo_labels(file_path):
    names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', ',', '?', '!', '@']
    entries = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            class_id = int(float(parts[0]))
            x_center = float(parts[1])
            entries.append((x_center, class_id))
    
    entries.sort(key=lambda x: x[0])
    return ''.join([names[class_id] for x_center, class_id in entries])


def clean_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Не удалось удалить {file_path}. Причина: {e}')

def clean_up():
    for folder in [FOLDER_UPLOADS, FOLDER_PROCESSED]:
        clean_directory(folder)


if __name__ == "__main__":
    if CLEAN_UP_FILES:
        clean_up()
    os.makedirs(FOLDER_UPLOADS, exist_ok=True)
    os.makedirs(FOLDER_PROCESSED, exist_ok=True)
    os.makedirs(FOLDER_BOXED, exist_ok=True)
    os.makedirs(FOLDER_TRANSLATED, exist_ok=True)
    os.makedirs(FOLDER_LABELS, exist_ok=True)

    app.run(host="0.0.0.0", port=5000, debug=True)
