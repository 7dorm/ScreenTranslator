import os
import xml.etree.ElementTree as ET


def convert_xml_to_yolo(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Получаем имя изображения
    image_name = str(root.find('.//filename').text)[:-4]
    size_element = root.find('.//size')
    image_width = int(size_element.find('width').text)
    image_height = int(size_element.find('height').text)

    yolo_annotations = []
    for rect in root.findall('.//object'):
        class_name = rect.find('name').text

        # Извлекаем координаты
        bndbox = rect.find('bndbox')
        xmin = int(bndbox.find('xmin').text)
        ymin = int(bndbox.find('ymin').text)
        xmax = int(bndbox.find('xmax').text)
        ymax = int(bndbox.find('ymax').text)

        # Преобразование в формат YOLO
        x_center = ((xmin + xmax) / 2) / image_width
        y_center = ((ymin + ymax) / 2) / image_height
        width_yolo = (xmax - xmin) / image_width
        height_yolo = (ymax - ymin) / image_height

        yolo_annotations.append(f"{class_name} {x_center} {y_center} {width_yolo} {height_yolo}\n")

    return image_name, yolo_annotations


def save_yolo_txt(image_name, yolo_annotations, output_folder):
    txt_file = os.path.splitext(os.path.basename(image_name))[0] + '.txt'
    txt_path = os.path.join(output_folder, txt_file)

    with open(txt_path, 'w') as f:
        for annotation in yolo_annotations:
            f.write(annotation)


def main(xml_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    files = 0
    for xml_file in os.listdir(xml_folder):

        if xml_file.endswith('.xml'):
            files+=1
            xml_path = os.path.join(xml_folder, xml_file)
            image_name, yolo_annotations = convert_xml_to_yolo(xml_path)

            save_yolo_txt(image_name, yolo_annotations, output_folder)
            print(f"Converted {xml_file} to {os.path.basename(image_name)}.txt")
    print(files)


if __name__ == "__main__":
    # Путь к папке с XML файлами и к выходной папке
    xml_folder = '/Users/...'
    output_folder = '/Users/...'

    main(xml_folder, output_folder)