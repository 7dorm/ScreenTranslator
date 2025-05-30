import io
from PIL import Image
import pytest

import sys
from pathlib import Path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))
from ScreenTranslator.server.server import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_index(client):
    response = client.get("/")
    assert response.status_code == 200

def test_process_file_no_file(client):
    response = client.post("/ScreenTranslatorAPI/process")
    assert response.status_code == 400
    assert b"No file uploaded" in response.data

def test_process_file_invalid_file_type(client):
    data = {
        'File': (io.BytesIO(b"invalid content"), 'test.txt')
    }
    response = client.post("/ScreenTranslatorAPI/process", data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b"Invalid file type or size" in response.data

def test_process_file_invalid_params_json(client):
    # Create a dummy JPEG image in memory
    img = Image.new("RGB", (100, 100), color="red")
    byte_io = io.BytesIO()
    img.save(byte_io, format="JPEG")
    byte_io.seek(0)

    data = {
        'File': (byte_io, 'test.jpg'),
        'Params': '{"invalid_json":'  # malformed JSON
    }
    response = client.post("/ScreenTranslatorAPI/process", data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b"Invalid Params JSON" in response.data