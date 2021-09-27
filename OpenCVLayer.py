import numpy as np
import cv2

#Returns positions of all faces. No faces returns None
def find_face(grayImg):
    haarFrontFace = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    #Change these parameters for better preformances
    faceRects = haarFrontFace.detectMultiScale(grayImg, scaleFactor = 1.2, minNeighbors = 5);
    return faceRects


#Return the first found face. Return none if no faces found
def crop_params(img, buffer):
    cvImg = np.array(img)
    params = find_face(cvImg)

    if len(params) == 0:
        return None

    x,y,w,h = params[0]
    #Return tuple: x,y; w,h; buffer
    return x,y,w,h,int(buffer)/2
