from PIL import Image

filename = 'images.jpeg'

with Image.open("images.jpeg") as img:
    img.load()

print( int('%02x%02x%02x' % img.getpixel((0, 0)), 16))
