from typing import Union
from ultralytics.utils.plotting import Annotator, colors

import cv2
import numpy as np
import os
from PIL import Image, ImageFont
from PIL import ImageDraw


def convert_to_pil_image(image: Union[cv2.Mat, np.ndarray]) -> Image.Image:
    if isinstance(image, cv2.Mat):
        image = image.get()  # Convert Mat to ndarray
    elif not isinstance(image, np.ndarray):
        raise TypeError("Input must be a OpenCV Mat or NumPy ndarray.")

    # Convert from BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Convert to PIL Image
    pil_image = Image.fromarray(image)
    return pil_image

def convert_pil_to_cv(image: Image.Image, to_mat: bool = False) -> Union[cv2.Mat, np.ndarray]:
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Convert PIL Image to NumPy ndarray
    image_np = np.array(image)

    # Convert from RGB to BGR for OpenCV
    image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

    if to_mat:
        # Convert ndarray to OpenCV Mat
        mat_image = cv2.Mat(image_np)
        return mat_image
    else:
        return image_np

def resize_image(image: Image.Image, size: tuple[int, int] = None):
    if size:
        lsize = image.size
        k = size[0] / lsize[0]
        image = image.resize((round(lsize[0] * k), round(lsize[1] * k)))
    print(image.size)
    return image

def write_text_on_image(image, text: str,
                        position: tuple = (10, 10), font_path: str = None,
                        font_size: int = 100, color: tuple = (255, 255, 255),
                        shadow_color: tuple = None, shadow_offset: tuple = (2, 2)):
    # Open the image
    image = image.convert('RGBA')  # Ensure the image has an alpha channel

    # Initialize ImageDraw
    draw = ImageDraw.Draw(image)

    # Load the font
    if font_path:
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            print(f"Font file not found or invalid: {font_path}. Using default font.")
            font = ImageFont.load_default()
    else:
        font = ImageFont.load_default()

    # If shadow_color is specified, draw the shadow first
    if shadow_color:
        draw.text((position[0] + shadow_offset[0], position[1] + shadow_offset[1]),
                  text, font=font, fill=shadow_color)

    # Draw the main text
    draw.text(position, text, font=font, fill=color)

    # Save the image
    return image

def draw_bounding_box(image1, data, text,
                      output_path='output.jpg',
                      box_color='red',
                      box_thickness=5):
    x_min, y_min, x_max, y_max = [data[i] for i in data]
    try:
        # Open the image
        image = image1.convert("RGB")
        x_min, x_max = x_min * image.size[0], x_max * image.size[0]
        y_min, y_max = y_min * image.size[1], y_max * image.size[1]

        draw = ImageDraw.Draw(image)

        # Define the bounding box coordinates
        bounding_box = [(x_min, y_min), (x_max, y_max)]

        # Draw the bounding box
        draw.rectangle(bounding_box, outline=box_color, width=box_thickness)
        image = write_text_on_image(image, text, (x_min, y_max + 20))
        
        return image
    except FileNotFoundError:
        print(f"Error: The file {image} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return image1

def draw_bounding_boxes(image, data, box_thickness=2, box_color="red"):
    keys = list(data.keys())
    for i in keys:
        image = draw_bounding_box(image, data[i], i, box_thickness=box_thickness, box_color=box_color)
    return image

def draw_boxes_ultralytics(image: Image.Image, labels) -> Image.Image:
    image_np = np.array(image)
    annotator = Annotator(image_np, line_width=1, font_size=1)
    palette_size = 50

    for item in labels:
        for label, box in item.items():
            x1 = int(box['x_min'] * image.width)
            y1 = int(box['y_min'] * image.height)
            x2 = int(box['x_max'] * image.width)
            y2 = int(box['y_max'] * image.height)
            conf = box.get('confidence')
            txt = f"{label} {conf:.2f}" if conf is not None else label

            class_index = hash(label) % palette_size
            color = colors(class_index, bgr=False)

            annotator.box_label([x1, y1, x2, y2], txt, color=color)

    return Image.fromarray(annotator.result())

