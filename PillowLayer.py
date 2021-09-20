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
    #Start by getting a size for the crop
    newWidth = None
    newHeight = None
    width, height = image.size
    if len(params.get('NUMBERS',[])) == 2:
        newWidth = params['NUMBERS'][0]
        newHeight = params['NUMBERS'][1]

    #Put in some defaults if no crop size specified
    if newWidth is None or newHeight is None:
        newWidth = int(width / 2)
        newHeight = int(height / 2)

    # positions can be: center, topleft, topright, bottomleft, bottomright
    # Seems that 0,0 is topleft -> set that as default
    startSide = params.get('SIDE', "center")
    #Make center the default
    middle = int(width/2)
    left = middle - int(newWidth / 2)
    right = middle + int(newWidth / 2)

    middle = int(height/2)
    bottom = middle + int(newHeight / 2)
    top = middle - int(newHeight / 2)

    #Make specified movements:
    if 'DOWN' in params:
        bottom = height
        top = height - newHeight

    elif 'UP' in params:
        bottom = newHeight
        top = 0

    if startSide.lower() == "right":
        right = width
        left = width - newWidth

    elif startSide.lower() == "left":
        right = newWidth
        left = 0

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

def show(image, params, deps):
    return image
