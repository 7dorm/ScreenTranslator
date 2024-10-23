import os

def rename_files(directory):
    # Получаем список файлов в указанной директории
    files = os.listdir(directory)
    
    # Фильтруем только файлы (игнорируем папки)
    files = [f for f in files if os.path.isfile(os.path.join(directory, f))]
    
    # Переименовываем файлы
    for i, file_name in enumerate(files, start=1):
        # Создаем новое имя файла
        new_name = f"PART_OF_THE_NAME_{i}{os.path.splitext(file_name)[1]}"
        
        # Полные пути для старого и нового имен
        old_file_path = os.path.join(directory, file_name)
        new_file_path = os.path.join(directory, new_name)
        
        # Переименование файла
        os.rename(old_file_path, new_file_path)
        print(f"Переименован: '{old_file_path}' -> '{new_file_path}'")

# Укажи путь к директории, которую нужно обработать
directory_path = 'DIRECTORY_PATH'
rename_files(directory_path)
