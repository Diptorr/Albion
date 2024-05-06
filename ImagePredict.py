from ultralytics import YOLO

# Load a model
model = YOLO('best(1).pt')  # pretrained YOLOv8n model

# Run batched inference on a list of images
screenx_center = 1920/2
screeny_center = 1080/2

decision = {
    "cotton_II": False,
    "cotton_III": False,
    "cotton_IV": False,
    "player": False,
    "depleeted_cotton_II": False,
    "depleeted_cotton_III": False,
    "depleeted_cotton_IV": False,
    "mount": False,
}

results = model(['test2.png'], conf=.20, save=True)  # return a list of Results objects
boxes = results[0].boxes.xyxy.tolist()
classes = results[0].boxes.cls.tolist()
names = results[0].names
confidences = results[0].boxes.conf.tolist()

# Process results list
for box, cls, conf in zip(boxes, classes, confidences):
    x1, y1, x2, y2 = box
    
    center_x = (x1+x2) / 2
    center_y = (y1+y2) / 2

    confidence = conf
    detected_class = cls
    name = names[int(cls)]
    
    if name=="depleeted_cotton_II":
        decision["depleeted_cotton_II"] = True
        decision["depleeted_cotton_II_location"] = (center_x, center_y)
    elif name == "depleeted_cotton_III":
        decision["depleeted_cotton_III"] = True
        decision["depleeted_cotton_III_location"] = (center_x, center_y)
    elif name == "depleeted_cotton_IV":
        decision["depleeted_cotton_IV"] = True
        decision["depleeted_cotton_IV_location"] = (center_x, center_y)
    elif name == "player":
        decision["player"] = True
        decision["player_location"] = (center_x, center_y)
    elif name == "mount":
        decision["mount"] = True
        decision["mount_location"] = (center_x, center_y)
    elif name == "cotton_II":
        decision["cotton_II"] = True
        distance = ((center_x - screenx_center) ** 2 + (center_y - screeny_center) **2) **.5
        if "cotton_II_location" in decision:
            # Calculate if closer
            if distance < decision["cotton_II_distance"]:
                decision["cotton_II_location"] = (center_x, center_y)
                decision["cotton_II_distance"] = distance
        else:
            decision["cotton_II_location"] = (center_x, center_y)
            decision["cotton_II_distance"] = distance
    elif name == "cotton_III":
        decision["cotton_III"] = True
        distance = ((center_x - screenx_center) ** 2 + (center_y - screeny_center) **2) **.5
        if "cotton_III_location" in decision:
            # Calculate if closer
            if distance < decision["cotton_III_distance"]:
                decision["cotton_III_location"] = (center_x, center_y)
                decision["cotton_III_distance"] = distance
        else:
            decision["cotton_III_location"] = (center_x, center_y)
            decision["cotton_III_distance"] = distance
    elif name == "cotton_IV":
        decision["cotton_IV"] = True
        distance = ((center_x - screenx_center) ** 2 + (center_y - screeny_center) **2) **.5
        if "cotton_II_location" in decision:
            # Calculate if closer
            if distance < decision["cotton_IV_distance"]:
                decision["cotton_IV_location"] = (center_x, center_y)
                decision["cotton_IV_distance"] = distance
        else:
            decision["cotton_IV_location"] = (center_x, center_y)
            decision["cotton_IV_distance"] = distance
    
print(decision)