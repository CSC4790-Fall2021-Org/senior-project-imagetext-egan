'''

Layer between the text processing code and image changing code
The objective of this file is to handle the general image work that
will need to be done whenever a command is called.
It shoudl also be able to check for exceptions so when Pillow or
OpenCV is called there is no chance of an error occuring.

'''

import os
import glob
from PIL import Image
import PillowLayer
import Values

class ImageLayer:

    def __init__(self):
        self.PATH = "./Pictures/"
        self.workingImage = "therock.jpg"
        #See if working w/OpenCV[0] or Pillow[1]
        #Default to pillow, use OpenCV when dealing w/specific elements
        self.workingStyle = 1
        self.currImg = Image.open(self.PATH + self.workingImage)
        self.lastImg = [(self.workingImage, self.currImg)]

    def commandHandler(self, method, adjs, objs, params):
        #Find the image we want to deal with
        exist = False
        for element in objs:
            exist = self.imgExists(element)

            #IF exist = false, might use OpenCV
            if exist != False and exist != self.workingImage:
                self.workingImage = exist
                self.currImg = Image.open(self.PATH + exist)
            elif exist == False:
                if element in Values.cvKeywords:
                    params["SPECIAL"] = method
                if element in Values.kwParams:
                    params["SPARAMS"] = element

        if method == "reset" or method == "revert":
            self.currImg = Image.open(self.PATH + self.workingImage)

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


    def showImage(self):
        if self.workingStyle == 1:
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
        self.currImg = Image.open(self.PATH + self.workingImage)
        print("Updated default image.")

    #Return file if it exists, else return false
    #BUG: should only return if imagename exists?
    def imgExists(self, imgName):
        imgName = imgName.lower().strip()
        for file in glob.glob(self.PATH + "/*.*"):
            name = os.path.basename(file).lower()
            if name == imgName or name.split('.')[0] == imgName:
                return os.path.basename(file)
        return False
