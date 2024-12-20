import os
import shutil
from PIL import Image, ImageOps

def process_files(input_dir, output_dir):
    """
    Обрабатывает все файлы из папки input_dir, инвертируя изображения .jpg
    и копируя остальные файлы в output_dir, сохраняя структуру подпапок.

    :param input_dir: Путь к исходной папке с файлами.
    :param output_dir: Путь к папке для сохранения файлов.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Обработка папки: {input_dir}")

    for root, _, files in os.walk(input_dir):
        # Вычисляем относительный путь текущей папки
        rel_path = os.path.relpath(root, input_dir)
        output_subdir = os.path.join(output_dir, rel_path)

        if not os.path.exists(output_subdir):
            os.makedirs(output_subdir)

        print(f"\nОбработка подпапки: {root}")
        print(f"Найдено файлов: {len(files)}")

        for file in files:
            input_file = os.path.join(root, file)
            output_file = os.path.join(output_subdir, file)

            try:
                if file.lower().endswith(".jpg"):
                    #print(f"  Инверсия изображения: {input_file}")
                    with Image.open(input_file) as img:
                        inverted_image = ImageOps.invert(img.convert("RGB"))
                        inverted_image.save(output_file)
                        #print(f"    Сохранено: {output_file}")
                else:
                    #print(f"  Копирование файла: {input_file}")
                    shutil.copy2(input_file, output_file)
                    #print(f"    Сохранено: {output_file}")
            except Exception as e:
                print(f"    Ошибка обработки файла {input_file}: {e}")

if __name__ == "__main__":
    input_directory = "dataset"
    output_directory = "invdata"

    if not os.path.exists(input_directory):
        print(f"Ошибка: Папка {input_directory} не найдена.")
    else:
        process_files(input_directory, output_directory)
