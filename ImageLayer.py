'''

Layer between the text processing code and image changing code
The objective of this file is to handle the general image work that
will need to be done whenever a command is called.
It shoudl also be able to check for exceptions so when Pillow or
OpenCV is called there is no chance of an error occuring.

'''

import os
import io
import glob
from PIL import Image
import PillowLayer
import Values

class ImageLayer:

    def __init__(self, path="./Pictures/", workingImage="therock.jpg"):
        self.path = path
        self.workingImage = workingImage
        self.currImg = Image.open(self.path + self.workingImage)
        self.lastImg = [(self.workingImage, self.currImg)]

    def commandHandler(self, method, adjs, objs, params):
        #Find the image we want to deal with
        exist = False
        for element in objs:
            exist = self.imgExists(element)

            #IF exist = false, might use OpenCV
            if exist != False and exist != self.workingImage:
                self.workingImage = exist
                self.currImg = Image.open(self.path + exist)
            elif exist == False:
                if element in Values.cvKeywords:
                    params["SPECIAL"] = method
                if element in Values.kwParams:
                    params["SPARAMS"] = element

        if method == "reset" or method == "revert":
            self.currImg = Image.open(self.path + self.workingImage)

        elif method == "set":
            if exist != False:
                self.setDefault(exist)
            else:
                print("Could not find image.")
                return False
        elif method == "undo":
            self.undoImage()
        else:
            self.currImg = PillowLayer.getMethod(method, adjs, params, self.currImg)

        return True

    def returnImage(self):
        #Convert to Byte array -> Necessary for Flask
        self.img_byte_arr = io.BytesIO()
        self.currImg.save(self.img_byte_arr, format='PNG')
        self.img_byte_arr.seek(0)
        return self.img_byte_arr

    def showImage(self):
        self.currImg.show()

    def setUndo(self):
        self.lastImg.append((self.workingImage, self.currImg))

    def undoImage(self):

        if not self.lastImg or len(self.lastImg) <= 1:
            self.workingImage, self.currImg = self.lastImg.pop()
            print("Cannot undo further.")
        else:
            self.lastImg.pop()
            self.workingImage, self.currImg = self.lastImg.pop()

    def setDefault(self, imgName):
        self.workingImage = imgName
        self.currImg = Image.open(self.path + self.workingImage)
        print("Updated default image.")

    #Return file if it exists, else return false
    #BUG: should only return if imagename exists?
    def imgExists(self, imgName):
        imgName = imgName.lower().strip()
        for file in glob.glob(self.path + "/*.*"):
            name = os.path.basename(file).lower()
            if name == imgName or name.split('.')[0] == imgName:
                return os.path.basename(file)
        return False

    def getFname(self):
        return self.workingImage

    def setImg(self, name):
        self.workingImage = name
        self.currImg = Image.open(self.path + name)
        self.lastImg = [(self.workingImage, self.currImg)]

    def setPath(self, p):
        self.path = p
