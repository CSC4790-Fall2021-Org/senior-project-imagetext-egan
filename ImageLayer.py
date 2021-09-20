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


class ImageLayer:

    def __init__(self):
        self.PATH = "./Pictures/"
        self.WORKING_IMAGE = "Koala.jpg"
        #See if working w/OpenCV[0] or Pillow[1]
        #Default to pillow, use OpenCV when dealing w/specific elements
        self.workingStyle = 1
        self.currImg = Image.open(self.PATH + self.WORKING_IMAGE)
        self.lastImg = Image.open(self.PATH + self.WORKING_IMAGE)


    def commandHandler(self, method, deps, params):
        #Find the image we want to deal with
        if "dobj" in deps:
            exist = self.imgExists(deps["dobj"])
            #IF exist = false, might use OpenCV
            if exist != False:
                self.WORKING_IMAGE = exist
                self.currImg = Image.open(self.PATH + exist)

        if method == "reset":
            self.currImg = Image.open(self.PATH + self.WORKING_IMAGE)
        elif method == "rollback":
            self.currImg = self.lastImg
        else:
            self.lastImg = self.currImg
            self.currImg = PillowLayer.getMethod(method, deps, params, self.currImg)


    def showImage(self):
        if self.workingStyle == 1:
            self.currImg.show()

    def setDefault(self, imgName):
        fileExists = self.imgExists(imgName)
        if(fileExists != False):
            self.WORKING_IMAGE = fileExists
            self.currImg = Image.open(self.PATH + self.WORKING_IMAGE)
            print("Updated default image.")
            return True
        print("Could not find image %s." % imgName.strip())
        return False

    #Return file if it exists, else return false
    def imgExists(self, imgName):
        for file in glob.glob(self.PATH + "/*.*"):
            if os.path.basename(file).lower().startswith(imgName.lower().strip()):
                return os.path.basename(file)
        return False
