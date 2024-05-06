import cv2 as cv
import numpy as np

yolo = cv.dnn.readNet('best(1).pt')

classes = {
    "cotton_II": False,
    "cotton_III": False,
    "cotton_IV": False,
    "player": False,
    "depleeted_cotton_II": False,
    "depleeted_cotton_III": False,
    "depleeted_cotton_IV": False,
}
len(classes)
img= cv.imread("test2.png")
blob = cv.dnn.blobFromImage(img, 1/255, (320,320), (0, 0, 0), swapRB=True, crop= False)
image = blob[0].reshape(320,320,1)

yolo.setInput(blob)

output_layer_name = yolo.getUnconnectedOutLayersNames()
layeroutput = yolo.forward(output_layer_name)
boxes = []
confidence = []
class_ids = []

for output in layeroutput:
    for detection in output:
        score = detection[5:]
        calss_id = np.argmax(score)
        confidence = score[class_id]