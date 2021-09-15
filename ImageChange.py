from PIL import Image, ImageOps, ImageFilter
import os
import math


#Here are some of the modifiers we're looking for:
modify_more = ("lot", "greatly", "more", "significantly", "really", "substantially")
modify_less = ("little", "slightly", "less", "bit", "lightly", "somewhat")

# Functions related to the ways an image can change
# Function names are lemmatized versions of the words
# Each function takes optional args, returns new image
# Function can be passed dictionary of options and tries to find them
def getMethod(methodName, deps, parameters, image):
    #Will always pass, image and tuple -> [parameters, deps]
    return eval(methodName)(image, parameters, deps)

# Needs an image, can have new size, startSideition,
def crop(image, params, deps):
    #Unpack and look for -> width, height, SECTION, SIDES
    width = None
    height = None
    if 'NUMBERS' in params:
        if len(params['NUMBERS']) == 2:
            width = params['NUMBERS'][0]
            height = params['NUMBERS'][1]
    startSide = params['SIDES'] if 'SIDES' in params else "center"
    startSection = params['SECTION'] if 'SECTION' in params else None

    if width is None or height is None:
        width = int(image.size[0] / 2)
        height = int(image.size[1] / 2)
    # positions can be: center, topleft, topright, bottomleft, bottomright
    # Seems that 0,0 is topleft
    # im.crop((left, top, right, bottom))
    top = 0
    left = 0
    bottom = height
    right = width
    if startSide == "center":
        middle = image.size[0] - width
        left = middle - int(width / 2)
        right = middle + int(width / 2)
        middle = image.size[1] - height
        bottom = middle + int(height / 2)
        top = middle - int(height / 2)
    else:
        if startSection.lower() == "bottom":
            bottom = image.size[1]
            top = image.size[1] - height
        if startSide.lower() == "right":
            right = image.size[0]
            left = image.size[0] - width

    return image.crop((left, top, right, bottom))


# Needs an image, can have a blur percentage
def blur(image, params, deps):
    pct = int(params['PERCENT']) if 'PERCENT' in params else None
    if pct is None:
        #Check to see if they used modifiers
        if deps.get("modifier", None) in modify_more:
            pct = 60
        elif deps.get("modifier", None) in modify_less:
            pct = 15
        else:
            return image.filter(ImageFilter.BLUR)
    # Formula: min(x,y)/20 * pct^2/100^2 b/c blur uses radius
    blurFormula = min(image.size[0], image.size[1]) / 20 * math.pow(pct, 2) / 10000
    return image.filter(ImageFilter.GaussianBlur(radius=blurFormula))

def grayscale(image, params, deps):

    return ImageOps.grayscale(image)

def invert(image, params, deps):

    return ImageOps.invert(image)

def enhance(image, params, deps):

    if deps.get("modifier", None) in modify_more:
        return image.filter(ImageFilter.EDGE_ENHANCE_MORE)

    return image.filter(ImageFilter.EDGE_ENHANCE)

def emboss(image, params, deps):

    return image.filter(ImageFilter.EMBOSS)

def smooth(image, params, deps):

    if deps.get("modifier", None) in modify_more:
        return image.filter(ImageFilter.SMOOTH_MORE)

    return image.filter(ImageFilter.SMOOTH)

def sharpen(image, params, deps):

    return image.filter(ImageFilter.SHARPEN)

def rotate(image, params, deps):

    degrees = 180

    if len(params.get('NUMBERS',[])) == 1:
            degrees = params['NUMBERS'][0]
    elif deps.get("modifier", None) in modify_more:
        degrees = 270
    elif deps.get("modifier", None) in modify_less:
        degrees = 30

    return image.rotate(degrees, expand=True)
