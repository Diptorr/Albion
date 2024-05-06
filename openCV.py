import cv2 as cv
from ultralytics import YOLO
import pyautogui
import numpy as np
from PIL import Image
import os

class WindowsCapture:
 w = 0
 h = 0
 hwnd = None

class ImageProccessor:
    w = 0
    h = 0
    net = None
    ln = None
    calsses = {}
    colors = []

    def __init__(self, image_size, model):
        np.random.seed(42)
        self.net = cv.dnn.readNetFromDarknet(model)
        self.net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
        self.ln = self.net.getLayerNames()
        self.ln = [self.ln[i-1] for i in self.net.getUnconnectedOutLayers()]
        self.W = image_size[0]
        self.H = image_size[1]

        lines = {"cotton_II": False,
    "cotton_III": False,
    "cotton_IV": False,
    "player": False,
    "depleeted_cotton_II": False,
    "depleeted_cotton_III": False,
    "depleeted_cotton_IV": False,}

    def proccess_image(self, image):
        blob = cv.dnn.blobFromImage(image, 1/255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        outputs = self.net.forward(self.ln)
        outputs = np.vstack(outputs)

        coordinates = self.get_coorinates(outputs, 0.5)
        
        self.draw_idemtified_object(image, coordinates)

        return coordinates
    
    def get_coordinates(self, outputs, conf):
        boxes = []
        confidences = []
        calssIds = []

        for output in outputs:
            scores = output[5:]

            classID = np.argmax(scores)
            confidence = scores[classID]
            if confidence > conf:
                x, y, w, h = output[4:] * np.array([self.W, self.H,self.W, self.H])
                p0 = int(x - w//2), int(y - h//2)
                boxes.append([*p0, int(w), int(h)])
                confidences.append(float(confidence))
                calssIds.append(classID)

        indices = cv.dnn.NMSBoxes(boxes, confidences, conf, conf-0.1)

        if len(indices) == 0:
            return []
        
        coordinates = []
        for i in indices.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])

            coordinates.append({'x': x, 'y': y, 'w': w, 'h': h, 'class': calssIds[i], 'class_name': self.classes[calssIds[i]]})
        return coordinates
    def draw_identified_objects(self, image, coordinates):
        for coordinate in coordinates:
            x = coordinate['x']
            y = coordinate['y']
            w = coordinate['w']
            h = coordinate['h']
            classID = coordinate['class']

            color =self.colors[classID]

            cv.rectangle(image, (x, y), (x + w, y + h), color, 2)
            cv.putText(image, self.classes[classID], (x, y -10), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        cv.imshow('window', image)
window_name = ""
model = YOLO('best(1).pt')

wincap = WindowsCapture(window_name)
improc = ImageProccessor(wincap.get_window_size(), model)

while(True):
    ss = wincap.get_screenshot()

    coordinates = improc.proccess_image(ss)


