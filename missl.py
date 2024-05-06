import pyautogui
print('Press Ctrl-C to quit.')
try:
    while True:
        x, y = pyautogui.position()
        positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
        print(positionStr, end='')
        print('\b' * len(positionStr), end='', flush=True)
except KeyboardInterrupt:
    print('\n')



def mount_up(decision_mount, processing_time_mount): 
    if decision_mount["mount"]:
            pyautogui.click(decision_mount["mount_location"])
            distance_target = decision_mount["mount_distance"]
            print("Going to mount: ", decision_mount["mount_location"])
            pyautogui.PAUSE = int(distance_target) / 180 - processing_time_mount           
    else:
        pyautogui.click(900, 540)
        take_screenshot_mount(stop_event, model)
    take_screenshot(stop_event, model)   

def run_bot(decision, processing_time_mount):
    global i
    mount_location = None
    cotton_locations = ["mount"]
    for cotton_type in cotton_locations:
        if decision[cotton_type]:
            location = decision[cotton_type + "_location"]
            distance = decision[cotton_type + "_distance"]
            if distance < closest_cotton_distance:
                mount_location = location
                closest_cotton_distance = distance

    if mount_location:
        wait_time = closest_cotton_distance / 120 
        wait_time -= processing_time_mount  
        wait_time = max(0, wait_time)  
        pyautogui.click(mount_location)
        print(f"Going to closest cotton at {mount_location}. Waiting for {wait_time:.2f} seconds.")
        pyautogui.PAUSE = wait_time
    else:
        depleted_cotton_locations = ["depleted_cotton_II", "depleted_cotton_III", "depleted_cotton_IV"]
        for depleted_cotton_type in depleted_cotton_locations:
            if decision[depleted_cotton_type]:
                location = decision[depleted_cotton_type + "_location"]
                print(f"Clicking on depleted {depleted_cotton_type} at {location}")
                pyautogui.click(location)
                return



def take_screenshot_mount(stop_event, model):
    pyautogui.FAILSAFE = False

    while not stop_event.is_set():
        decision_mount = {
            "mount": False,
        }

        # Start time of image processing
        start_time = time.time()

        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot = Image.frombytes('RGB', screenshot.size, screenshot.tobytes())
        
        # Image processing
        results = model([screenshot], conf=.50)
        boxes = results[0].boxes.xyxy.tolist()
        classes = results[0].boxes.cls.tolist()
        names = results[0].names
        confidences = results[0].boxes.conf.tolist()

        # Process results
        for box, cls, conf in zip(boxes, classes, confidences):
            x1, y1, x2, y2 = box
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            name = names[int(cls)]

            # Update decision dictionary based on object detection
            if name.startswith("depleted_cotton"):
                decision_mount[name] = True
                decision_mount[name + "_location"] = (center_x, center_y)
            elif name in ["cotton_II", "cotton_III", "cotton_IV"]:
                decision_mount[name] = True
                cotton_type = name
                distance = ((center_x - CENTER_X) ** 2 + (center_y - CENTER_Y) ** 2) ** 0.5
                if cotton_type + "_location" in decision_mount:
                    if distance < decision_mount[cotton_type + "_distance"]:
                        decision_mount[cotton_type + "_location"] = (center_x, center_y)
                        decision_mount[cotton_type + "_distance"] = distance
                else:
                    decision_mount[cotton_type + "_location"] = (center_x, center_y)
                    decision_mount[cotton_type + "_distance"] = distance

        # End time of image processing
        end_time = time()

        # Calculate duration and print
        processing_time_mount = end_time - start_time
        print(f"Image processing time: {processing_time_mount:.2f} seconds")

        mount_up(decision_mount, processing_time_mount)