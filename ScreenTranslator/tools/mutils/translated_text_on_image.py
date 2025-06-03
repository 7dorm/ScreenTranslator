import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from ScreenTranslator.constants import RESOURCES_ARIAL
import collections

def process_image(image: Image.Image, translation, lines) -> Image.Image:
    width, height = image.size
    trans = partition_translation(lines, translation)

    for idx, entry in enumerate(lines):
        for line, box in entry.items():
            crop_box = (
                int(box['x_min'] * width),
                int(box['y_min'] * height),
                int(box['x_max'] * width),
                int(box['y_max'] * height)
            )

            # Padding (можно включить при необходимости)
            padding = 0
            padded_crop_box = (
                max(0, crop_box[0] - padding),
                max(0, crop_box[1] - padding),
                min(width, crop_box[2] + padding),
                min(height, crop_box[3] + padding)
            )
            cropped_region = image.crop(padded_crop_box)
            blurred_region = cropped_region.filter(ImageFilter.GaussianBlur(radius=40))

            # Маска для размытия
            mask = Image.new('L', cropped_region.size, 0)
            draw = ImageDraw.Draw(mask)
            rect_coords = (
                int(padding / 2),
                int(padding / 2),
                cropped_region.size[0] - int(padding / 2),
                cropped_region.size[1] - int(padding / 2)
            )
            draw.rectangle(rect_coords, fill=255)
            mask = mask.filter(ImageFilter.GaussianBlur(radius=25))
            image.paste(blurred_region, (padded_crop_box[0], padded_crop_box[1]), mask)

            # Анализ цвета
            new_cropped_region = image.crop(crop_box)
            cropped_region_rgb = new_cropped_region.convert('RGB')
            pixels = np.array(cropped_region_rgb)
            average_color = np.mean(pixels, axis=(0, 1)).astype(int)
            pixels1 = list(cropped_region_rgb.getdata())
            color_counts = collections.Counter(pixels1)
            most_common_color = color_counts.most_common(1)[0][0]
            inverted_color = tuple(c ^ 255 for c in most_common_color)

            # Отрисовка текста
            draw = ImageDraw.Draw(image)
            font_size = max(int(crop_box[3] - crop_box[1]), 1)
            try:
                font = ImageFont.truetype(RESOURCES_ARIAL, font_size)
            except (OSError, IOError):
                print("Шрифт не найден, используется стандартный")
                font = ImageFont.load_default()

            text = ' '.join(trans[idx])
            text_length = draw.textlength(text, font=font)
            if text_length > crop_box[2] - crop_box[0]:
                font_size = max(int(font_size * (crop_box[2] - crop_box[0]) / text_length), 1)
                try:
                    font = ImageFont.truetype(RESOURCES_ARIAL, font_size)
                except (OSError, IOError):
                    font = ImageFont.load_default()

            text_length = draw.textlength(text, font=font)
            text_position = (
                int(crop_box[0] + (crop_box[2] - crop_box[0] - text_length) / 2),
                int(crop_box[1] + (crop_box[3] - crop_box[1] - font_size) / 2)
            )

            draw.text(text_position, text, font=font, fill=(0, 0, 0), stroke_width=2, stroke_fill=(0, 0, 0))
            draw.text(text_position, text, font=font, fill=inverted_color)

    return image


def partition_translation(lines, translation):
    lines_len = len(lines)
    arr_translation = translation.split()
    translation_len = len(arr_translation)
    words_in_line = round(translation_len / lines_len)
    result = []
    for i in range(lines_len):
        result.append([])
        for j in range(words_in_line):
            if i * words_in_line + j + 1 <= translation_len:
                result[i].append(arr_translation[i * words_in_line + j])
    tm = 2
    i = lines_len-1
    j = words_in_line-1
    while i * words_in_line + j + tm <= translation_len:
        result[i].append(arr_translation[i * words_in_line + j + tm - 1])
        tm += 1
    return result



# file = "/Users/msansdu/Desktop/image_dataframe5.txt"
# d = pd.read_csv(file, sep="\s+", header=0)
# создали таблицу данных df
# df1 = pd.DataFrame(data=d)

if __name__ == "__main__":

    img = Image.open("/Users/deu/Desktop/test.jpg")
    t = {'M': {'x_min': 0.0, 'y_min': 0.019669771194458008, 'x_max': 0.023063499480485916, 'y_max': 0.06671099364757538}, '4EBG': {'x_min': 0.9268617630004883, 'y_min': 0.31449469923973083, 'x_max': 1.0, 'y_max': 0.3570478856563568}, 'NO': {'x_min': 0.1333111822605133, 'y_min': 0.3914007246494293, 'x_max': 0.2774268686771393, 'y_max': 0.5403369069099426}, 'FRIENDS': {'x_min': 0.29321807622909546, 'y_min': 0.4027039110660553, 'x_max': 0.6785239577293396, 'y_max': 0.5434397459030151}, 'DTD': {'x_min': 0.4119016230106354, 'y_min': 0.5753546357154846, 'x_max': 0.5059840679168701, 'y_max': 0.6139184832572937}}
    result_image = process_image(img, 'Привет чмо Нет друзей', t)
    result_image.show()


# lines1 = {'YOUR GUIDE': {'x_min': 0.3609338104724884, 'y_min': 0.1815936267375946, 'x_max': 0.6420243382453918, 'y_max': 0.28683874011039734},
#           'TO BILLBOARD': {'x_min': 0.33611077070236206, 'y_min': 0.2857617139816284, 'x_max': 0.6656801104545593, 'y_max': 0.38535046577453613},
#           'MARKETING': {'x_min': 0.36485782265663147, 'y_min': 0.38505563139915466, 'x_max': 0.6396201848983765, 'y_max': 0.48255202174186707}}
# result_image = process_image(img, "ваш гайд для маркетинга биллбордов", lines1)
# result_image.save("/Users/msansdu/Desktop/b1_copy1.jpg")
#
# img = Image.open("/Users/msansdu/Desktop/b2.jpg")
# lines2 = {'NO FRIENDS?!': {'x_min': 0.13535138964653015, 'y_min': 0.3922343850135803,  'x_max': 0.7655435800552368, 'y_max': 0.5439310073852539}}
# result_image = process_image(img, "нет друзей?!", lines2)
# result_image.save("/Users/msansdu/Desktop/b2_copy1.jpg")
#
# lines2 = {'NO FRIENDS?!': {'x_min': 0.13535138964653015, 'y_min': 0.3922343850135803,  'x_max': 0.7655435800552368, 'y_max': 0.5439310073852539}}
# process('/Users/msansdu/Desktop/b2.jpg', "нет друзей?!", lines2)
# lines3 = { 'NEED I SAY MORE?': {'x_min': 0.029666077345609665, 'y_min': 0.8832525014877319, 'x_max': 0.9755286574363708, 'y_max': 0.9924886226654053}}
# process('/Users/msansdu/Desktop/b3.jpg', "надо мне сказать больше?", lines3)
# lines4 = {'HAPPY': {'x_min': 0.1424936205148697, 'y_min': 0.10930764675140381, 'x_max': 0.43642741441726685, 'y_max': 0.25053876638412476},
#            'BIKTHDAY': {'x_min': 0.14356505870819092, 'y_min': 0.26212283968925476, 'x_max': 0.4239271879196167, 'y_max': 0.3469827473163605}}
# process('/Users/msansdu/Desktop/hb.jpg', "с днем рождения", lines4)