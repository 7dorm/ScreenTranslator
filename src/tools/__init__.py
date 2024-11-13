import os

def find_file_by_name(directory, file_name):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file)[0] == file_name:  # Check name without extension
                return os.path.join(root, file)
    return None
