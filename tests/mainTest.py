from ScreenTranslator.tools.Medipy import *
from ScreenTranslator.API import *
import pathlib
import os, sys
import pytest

# Windovod issue
if sys.platform == "win32":
    pathlib.PosixPath = pathlib.WindowsPath

FOLDER_RESOURCES = os.path.join(Path(__file__).resolve().parent, "resources")

def test_API():
    request = API_Request(os.path.join(FOLDER_RESOURCES, "cat.jpg"))
    response = API_Process(request)
    print("\n\n!!!!!!!!!!!!!!!!!!!!!\n\n")
    print(json.dumps(response.to_dict(), ensure_ascii=False, indent=4))
    print("\n\n!!!!!!!!!!!!!!!!!!!!!\n\n")

def test():
    assert True

if __name__ == "__main__":
    test_API()
