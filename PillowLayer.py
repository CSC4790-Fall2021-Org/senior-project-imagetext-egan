from PIL import Image, ImageOps, ImageFilter
import os
import math
import Values
import OpenCVLayer

# Functions related to the ways an image can change
def getMethod(methodName, adjs, parameters, image):
    #Will always pass, image and tuple -> [parameters, adjs]
    image = ImageOps.exif_transpose(image)
    return (eval(methodName)(image, parameters, adjs))

# Needs an image, can have new size, startSideition,
def crop(image, params, adjs):

    #See if this is a special crop
    if(params.get("SPECIAL", None) == "crop"):
        buffer = params.get('NUMBERS', [0])
        return crop_specific(image, OpenCVLayer.crop_params(ImageOps.grayscale(image),buffer[0]))

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

    # Seems that 0,0 is topleft
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

    return image.crop((left, top, right, bottom)), None


# Needs an image, can have a blur percentage
def blur(image, params, adjs):

    if(params.get("SPECIAL", None) == "blur"):
        buffer = params.get('NUMBERS', [0])
        aroundFace = params.get("SPARAMS", "None")
        return blur_face(image, params, adjs, buffer[0], aroundFace)

    pct = params.get('PERCENT', None)
    if pct is None:
        #Check to see if they used modifiers
        if adjs in Values.modify_more:
            pct = 60
        elif adjs in Values.modify_less:
            pct = 15
        else:
            return image.filter(ImageFilter.BLUR), None
    # Formula: min(x,y)/20 * pct^2/100^2 b/c blur uses radius
    blurFormula = min(image.size[0], image.size[1]) / 20 * math.pow(int(pct), 2) / 10000
    return image.filter(ImageFilter.GaussianBlur(radius=blurFormula)), None

def grayscale(image, params, adjs):

    return ImageOps.grayscale(image), None

def invert(image, params, adjs):

    return ImageOps.invert(image), None

def enhance(image, params, adjs):

    if adjs in Values.modify_more:
        return image.filter(ImageFilter.EDGE_ENHANCE_MORE), None

    return image.filter(ImageFilter.EDGE_ENHANCE), None

def emboss(image, params, adjs):

    return image.filter(ImageFilter.EMBOSS), None

def smooth(image, params, adjs):

    if adjs in Values.modify_more:
        return image.filter(ImageFilter.SMOOTH_MORE)

    return image.filter(ImageFilter.SMOOTH), None

def sharpen(image, params, adjs):

    return image.filter(ImageFilter.SHARPEN), None

def rotate(image, params, adjs):

    degrees = 180

    if len(params.get('NUMBERS',[])) == 1:
            degrees = params['NUMBERS'][0]
    elif adjs in Values.modify_more:
        degrees = 270
    elif adjs in Values.modify_less:
        degrees = 30

    return image.rotate(degrees, expand=True), None

def show(image, params, adjs):
    return image, None

######################## OpenCV Specific Functions ############################

def crop_specific(image, params):
    #Make sure a face was found
    warning = None
    if params is None:
        warning = "No faces found"
        return image, warning

    x,y,w,h = params

    return image.crop((x, y, x+w, y+h)), warning

def blur_face(image, params, adjs, buffer, aroundFace):
    #Blur around face
    warning = None
    if aroundFace == "around":
        blurred = blur(image, {'PERCENT' : params.get('PERCENT', None)}, adjs)
        newImg, warning = OpenCVLayer.blur_around_face(image, blurred, buffer)
        return Image.fromarray(newImg).convert('RGB'), warning
    #Blur out the face
    #Get an amount to blur it
    pct = params.get('PERCENT', None)
    if pct is None:
        #Check to see if they used modifiers
        if adjs in Values.modify_more:
            pct = 80
        elif adjs in Values.modify_less:
            pct = 20
        else:
            pct = 50
    buffer = params.get('NUMBERS', [0])
    #Check to see if all faces must be blurred
    blurAll = (aroundFace == "all")
    newImg, warning = OpenCVLayer.blur_face(image, int(pct), buffer[0], blurAll)
    return Image.fromarray(newImg).convert('RGB'), warning
