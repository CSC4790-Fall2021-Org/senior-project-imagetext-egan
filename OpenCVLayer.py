import numpy as np
import cv2
import dlib
from imutils import face_utils
import numpy.polynomial.polynomial as poly
#Returns positions of all faces. No faces returns None
def find_face_haar(grayImg):
    haarFrontFace = cv2.CascadeClassifier('./Dependencies/haarcascade_frontalface_default.xml')
    #Change these parameters for better preformances
    faceRects = haarFrontFace.detectMultiScale(grayImg, scaleFactor = 1.4, minNeighbors = 5);
    return faceRects

def find_face_dlib(grayImg):
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("./Dependencies/shape_predictor_68_face_landmarks.dat")
    #Face detections, we only want the first
    rect = detector(grayImg, 1)

    if len(rect) == 0:
        #No faces found
        return None

    rect = rect[0]

    shape = predictor(grayImg, rect)
    shape = face_utils.shape_to_np(shape)

    # Get x, y, w, h values for
    faceRect = face_utils.rect_to_bb(rect)
    #faceXY = zip(*shape)

    # loop over the (x, y)-coordinates for the facial landmarks
    # 1- 17 corresponds to jawline
    #34 corresponds to tip of the nose
    #Use jawline until about nose, then go for edge detection
    #Return rect coords as one tuple and face coords as another
    return (faceRect, shape)
#Return the first found face. Return None if no faces found
def crop_params(img, buffer):
    cvImg = np.array(img)
    params = find_face_haar(cvImg)

    if len(params) == 0:
        return None

    if buffer < 0:
        buffer = 0

    #Return tuple: x,y; w,h;
    return buffered_vals(params[0], buffer/2, cvImg.shape)

def blur_face(img, blurredImg, buffer):
    cvImg = np.array(img)
    blurred = np.array(blurredImg)
    grayscaled = cv2.cvtColor(cvImg, cv2.COLOR_BGR2GRAY)

    faceRect, faceXY = find_face_dlib(grayscaled)

    if buffer < 0:
        buffer = 0
    #Crop to just the face
    x, y, w, h = buffered_vals(faceRect, buffer/2, grayscaled.shape)

    grayscaled = grayscaled[y:y+h, x:x+w]

    #Apply canny edge detection
    grayscaled = cv2.Canny(grayscaled,100,200)

    #Time to overlay onto blurred image
    #Loop through every row in grayscaled looking for 255 val
    #Stop at nose tip -> 34
    #Mouth is 63
    split = faceXY[63][1] - y
    for row in range(0, split):
        start, end = 0, w-1

        while(grayscaled[row, end] != 255 and end > 0):
            end -= 1

        if end <= 0:
            continue

        #find first 255 val
        while(grayscaled[row, start] != 255):
            start += 1
        #see if it's worth keeping going
        if start == end:
            #No blur
            continue

        #Now we have values -> replace
        blurred[y+row, x+start:x+end] = cvImg[y+row, x+start:x+end]
    #Now use the jaw points
    #Make an equation
    '''
    coefs = poly.polyfit(faceX[:17], faceY[:17],8)
    theVals = poly.polyval([*range(x, x+w)], coefs)
    print(theVals)
    print(faceY[33])
    print(y)
    for index, value in enumerate(theVals):
        upperBound = int(min(value, y+h))

        blurred[faceY[33]:upperBound, x+index] = cvImg[faceY[33]:upperBound, x+index]
    '''
    routes = faceXY[:17]
    mask = np.zeros((cvImg.shape[0], cvImg.shape[1]))
    mask = cv2.fillConvexPoly(mask, np.array(routes), 1).astype(np.bool)
    blurred[mask] = cvImg[mask]

    return np.uint8(blurred)

def buffered_vals(params, buffer, size):
    x,y,w,h = params
    width, height = size

    newX = x - buffer
    newY = y - buffer
    newW = w + buffer*2
    newH = h + buffer*2

    x = newX if newX > 0 else 0
    y = newY if newY > 0 else 0
    w = newW if x+newW < width else width
    h = newH if y+newH < height else height

    return (int(x),int(y),int(w),int(h))
