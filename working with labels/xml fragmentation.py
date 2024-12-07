import xml.etree.ElementTree as ET
import os
from operator import index

# Путь к исходному XML файлу
input_file = '/Users/...'
# Папка для сохранения отдельных XML файлов
output_folder = '/Users/...'

# Создаем папку, если она не существует
os.makedirs(output_folder, exist_ok=True)

# Загружаем XML файл
tree = ET.parse(input_file)
root = tree.getroot()

# Перебираем все элементы <image>
for index, image in enumerate(root.findall('image')):
    # Создаем новый корневой элемент
    new_root = ET.Element('tagset')
    new_root.append(image)

    # Создаем дерево из нового корневого элемента
    new_tree = ET.ElementTree(new_root)

    # Формируем имя для нового файла
    name = str(image.find("imageName").text)[4:-4]
    output_file = os.path.join(output_folder, f'{name}.xml')

    # Сохраняем новый XML файл
    new_tree.write(output_file, encoding='utf-8', xml_declaration=True)

print(f'Разделение завершено. {index + 1} файлов сохранено в папке "{output_folder}".')
