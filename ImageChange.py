from PIL import Image, ImageOps, ImageFilter
import os
import math


# Functions related to the ways an image can change
# Function names are lemmatized versions of the words
# Each function takes optional args, returns new image
def getMethod(methodName, image):
    return eval(methodName)(image)

# Needs an image, can have new size, start_position,
def crop(image, width=-1, height=-1, start_pos="center"):

    if width < 0 or height < 0:
        width = int(image.size[0] / 2)
        height = int(image.size[1] / 2)
    # positions can be: center, topleft, topright, bottomleft, bottomright
    # Seems that 0,0 is topleft
    # im.crop((left, top, right, bottom))
    top, left = 0, 0
    bottom = height
    right = width
    if start_pos == "center":
        middle = image.size[0] - width
        left = middle - int(width / 2)
        right = middle + int(width / 2)
        middle = image.size[1] - height
        bottom = middle + int(height / 2)
        top = middle - int(height / 2)
    else:
        if start_pos.startswith("bottom"):
            bottom = image.size[1]
            top = image.size[1] - height
        if start_pos.endswith("right"):
            right = image.size[0]
            left = image.size[0] - width

    return image.crop((left, top, right, bottom))


# Needs an image, can have a blur percentage
def blur(image, pct=None):

    if pct is None:
        return image.filter(ImageFilter.BLUR)
    # Formula: min(x,y)/20 * pct^2/100^2 b/c blur uses radius
    blurFormula = min(image.size[0], image.size[1]) / 20 * math.pow(pct, 2) / 10000
    return image.filter(ImageFilter.GaussianBlur(radius=blurFormula))

def grayscale(image):

    return ImageOps.grayscale(image)

def rotate(image, degrees=180):

    return image.rotate(degrees, expand=True)
