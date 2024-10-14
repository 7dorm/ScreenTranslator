import os
import xml.etree.ElementTree as ET


def convert_xml_to_yolo(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Получаем имя изображения
    image_name = str(root.find('.//imageName').text)[:-4]
    resolution = root.find('.//Resolution')
    image_width = int(resolution.get('x'))
    image_height = int(resolution.get('y'))

    yolo_annotations = []
    class_id = 0
    for rect in root.findall('.//taggedRectangle'):
        class_id += 1

        x = int(rect.get('x'))
        y = int(rect.get('y'))
        width = int(rect.get('width'))
        height = int(rect.get('height'))

        # Преобразование в формат YOLO
        x_center = (x + width / 2) / image_width
        y_center = (y + height / 2) / image_height
        width_yolo = width / image_width
        height_yolo = height / image_height

        yolo_annotations.append(f"{class_id} {x_center} {y_center} {width_yolo} {height_yolo}\n")

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

    for xml_file in os.listdir(xml_folder):
        if xml_file.endswith('.xml'):
            xml_path = os.path.join(xml_folder, xml_file)
            image_name, yolo_annotations = convert_xml_to_yolo(xml_path)

            save_yolo_txt(image_name, yolo_annotations, output_folder)
            print(f"Converted {xml_file} to {os.path.basename(image_name)}.txt")


if __name__ == "__main__":
    # Путь к папке с XML файлами и выходной папке
    xml_folder = '/Users/msansdu/Documents/project/annotations/xml annotations'
    output_folder = '/Users/msansdu/Documents/project/annotations/yolo annotations'

    main(xml_folder, output_folder)