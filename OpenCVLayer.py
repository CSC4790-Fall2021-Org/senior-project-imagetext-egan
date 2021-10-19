import numpy as np
import cv2
import dlib
from imutils import face_utils

#Returns positions of all faces. No faces returns None
#FASTEST -> LEAST ACCURATE
def find_face_haar(grayImg):
    haarFrontFace = cv2.CascadeClassifier('./Dependencies/haarcascade_frontalface_default.xml')
    #Change these parameters for better preformances
    faceRects = haarFrontFace.detectMultiScale(grayImg, scaleFactor = 1.4, minNeighbors = 5);

    return faceRects

#SLOWEST -> MOST ACCURATE !!!REQUIRES GPU
'''
def find_face_nn(img):
    #Load neural network if looking for all faces
    detector = dlib.cnn_face_detection_model_v1("./Dependencies/mmod_human_face_detector.dat")
    results = detector(img, 1)
    boxes = list()
    for r in results:
        #Format x,y,w,h
        boxes.append(face_utils.rect_to_bb(r.rect))

    return boxes
'''
def just_faces_dlib(grayImg):
    detector = dlib.get_frontal_face_detector()
    results = detector(grayImg, 1)
    boxes = list()
    for r in results:
        #Format x,y,w,h
        boxes.append(face_utils.rect_to_bb(r))

    return boxes
#MEDIUM SPEED, MEDIUM ACCURACY
def find_face_dlib(grayImg):

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("./Dependencies/shape_predictor_68_face_landmarks.dat")
    #Face detections, we only want the first
    rect = detector(grayImg, 1)

    if len(rect) == 0:
        #No faces found
        return None, None

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
    faces = find_face_haar(cvImg)

    if len(faces) == 0:
        return None

    if buffer < 0:
        buffer = 0

    #Return tuple: x,y,w,h;
    return buffered_vals(faces[0], buffer/2, cvImg.shape)

def blur_face(img, blurPct, buffer, blurAll):
    cvImg = np.array(img)
    grayscaled = cv2.cvtColor(cvImg, cv2.COLOR_BGR2GRAY)

    if blurAll:
        faces = just_faces_dlib(grayscaled)
        if len(faces) == 0:
            print("Could not find any faces")
            return cvImg
    else:
        faces = find_face_haar(grayscaled)
        if len(faces) == 0:
            print("Could not find face")
            return cvImg
        faces = [faces[0]]

    if buffer < 0:
        buffer = 0

    for face in faces:
        x,y,w,h = buffered_vals(face, buffer/2, grayscaled.shape)

        #Divide face area up into N rects (Default of 10)
        numRects = 21 - int(20 * blurPct/100)
        xRects = np.linspace(x, x+w, numRects + 1, dtype="int")
        yRects = np.linspace(y, y+h, numRects + 1, dtype="int")
        #Loop through each rect and take the mean of that area:
        for i in range(1, len(yRects)):
            for j in range(1, len(xRects)):
                #Get starting and ending coordinates
                startXY = xRects[j - 1], yRects[i - 1]
                endXY = xRects[j], yRects[i]
                blurArea = cvImg[startXY[1]:endXY[1], startXY[0]:endXY[0]]
                (B, G, R) = [int(x) for x in cv2.mean(blurArea)[:3]]
                cv2.rectangle(cvImg, startXY, endXY, (B, G, R), -1)

    return np.uint8(cvImg)


def blur_around_face(img, blurredImg, buffer):
    cvImg = np.array(img)
    blurred = np.array(blurredImg)
    grayscaled = cv2.cvtColor(cvImg, cv2.COLOR_BGR2GRAY)

    faceRect, faceXY = find_face_dlib(grayscaled)

    if faceRect == None:
        print("No faces found.")
        return blurred

    if buffer < 0:
        buffer = 0
    #Crop to just the face
    x, y, w, h = buffered_vals(faceRect, buffer/2, grayscaled.shape)

    grayscaled = grayscaled[y:y+h, x:x+w]

    #Try blurring the image to improve edge detection -> not great
    #grayscaled = cv2.GaussianBlur(grayscaled,(3,3),cv2.BORDER_DEFAULT)

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

    #Use points to create a mask
    routes = faceXY[:17]
    faceTop = min(faceXY[19][1], faceXY[24][1])
    newPoints = [[faceXY[16][0], faceTop],[faceXY[0][0], faceTop]]
    #routes = np.append(routes, np.flipud(faceXY[18:27]), axis=0)
    routes = np.append(routes, newPoints, axis=0)
    mask = np.zeros((cvImg.shape[0], cvImg.shape[1]))
    mask = cv2.fillConvexPoly(mask, np.array(routes), 1).astype(np.bool)
    blurred[mask] = cvImg[mask]
    return np.uint8(blurred)

def buffered_vals(params, buffer, size):
    x,y,w,h = params
    height, width = size
    bufferWidth = int(buffer*2/3)

    newX = x - bufferWidth
    newY = y - buffer - int(buffer/5)
    newW = w + bufferWidth*2
    newH = h + buffer*2

    x = max(newX, 0)
    y = max(newY, 0)
    w = min(x+newW, width) - x
    h = min(y+newH, height) - y

    return (int(x),int(y),int(w),int(h))
