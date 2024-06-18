import cv2
from PIL import Image
import threading
import pyautogui
import keyboard
from PIL import Image
from ultralytics import YOLO
import pydirectinput
import time
from PIL import ImageGrab
import random


def is_green(pixel):
    # Define the green color range 
    green_min = (0, 100, 0)  # Minimum RGB values for green
    green_max = (50, 255, 50)  # Maximum RGB values for green

    # Check if the pixel falls within the green color range
    return all(green_min[i] <= pixel[i] <= green_max[i] for i in range(3))

# Function to find all green pixels on the screen
def find_green_pixels():
    green_pixels = []
    # Capture the entire screen
    screen = ImageGrab.grab()
    width, height = screen.size

    # Loop through each pixel in the screen
    for x in range(width):
        for y in range(height):
            # Get the RGB values of the pixel
            pixel = screen.getpixel((x, y))
            # Check if the pixel is green
            if is_green(pixel):
                green_pixels.append((x, y))

    return green_pixels

model = YOLO('best(1).pt')
stop_event = threading.Event()

def mount_up(decision_mount, processing_time): 
    if decision_mount["mount"]:
            pyautogui.click(decision_mount["mount_location"])
            distance_target = decision_mount["mount_distance"]
            print("Going to mount: ", decision_mount["mount_location"])
            if distance_target / 180 - processing_time > 0:
                pyautogui.PAUSE = int(distance_target) / 180  + 0.3
                take_screenshot(stop_event, model)
    else:
        pyautogui.press('a')
        pyautogui.PAUSE = 4
        take_screenshot(stop_event, model)      

def run_bot(decision, processing_time):
    const_x = 1.8
    if decision["cotton_IV"]:
        pyautogui.click(decision["cotton_IV_location"])
        distance_target = decision["cotton_IV_distance"]
        print("Going to cotton_IV: ", decision["cotton_IV_location"])
        pyautogui.PAUSE = (int(distance_target) / 180) + 2 + const_x
        take_screenshot_mount(stop_event, model)

    elif decision["cotton_III"]:
        pyautogui.click(decision["cotton_III_location"])
        distance_target = decision["cotton_III_distance"]
        print("Going to cotton_III: ", decision["cotton_III_location"])
        pyautogui.PAUSE = (int(distance_target) / 180) + 1.05 + const_x
        take_screenshot_mount(stop_event, model)

    elif decision["cotton_II"]:
        pyautogui.click(decision["cotton_II_location"])
        distance_target = decision["cotton_II_distance"]
        print("Going to cotton_II: ", decision["cotton_II_location"])
        pyautogui.PAUSE = (int(distance_target) / 180) + 0.3 + const_x
        take_screenshot_mount(stop_event, model)

    else:
        # If no cotton of type II, III, or IV is detected, find the closest cotton and click on it
        closest_cotton = None
        min_distance = float('inf')
        for key in ["cotton_II", "cotton_III", "cotton_IV"]:
            if decision[key]:
                distance = decision[key + "_distance"]
                if distance < min_distance:
                    closest_cotton = key
                    min_distance = distance

        if closest_cotton:
            pyautogui.click(decision[closest_cotton + "_location"])
            print(f"Going to closest {closest_cotton}: ", decision[closest_cotton + "_location"])
        else:
            # If no cotton detected, look for green pixels and click on one randomly
            green_pixels = find_green_pixels()
            if green_pixels:
                random_green_pixel = random.choice(green_pixels)
                print(f"Clicking on random green pixel at {random_green_pixel}")
                take_screenshot_mount(stop_event, model)
                pyautogui.click(random_green_pixel)
            else:
                print("No cotton or depleted cotton found. Clicking at default location.")
                pyautogui.PAUSE = 4
                pyautogui.click(500, 700)

        

# Function to take screenshots
def take_screenshot(stop_event, model):
    screenx_center = 1920/2
    screeny_center = 1080/2
    pyautogui.FAILSAFE = False

    while not stop_event.is_set():

        decision = {
    "cotton_II": False,
    "cotton_III": False,
    "cotton_IV": False,
    "player": False,
    "depleeted_cotton_II": False,
    "depleeted_cotton_III": False,
    "depleeted_cotton_IV": False,
}
        start_time = time.time()
        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot = Image.frombytes('RGB', screenshot.size, screenshot.tobytes())
        
        results = model([screenshot], conf=.60)  # return a list of Results objects
        boxes = results[0].boxes.xyxy.tolist()
        classes = results[0].boxes.cls.tolist()
        names = results[0].names
        confidences = results[0].boxes.conf.tolist()

        # Process results list
        for box, cls, conf in zip(boxes, classes, confidences):
            x1, y1, x2, y2 = box
            
            center_x = (x1+x2) / 2
            center_y = (y1+y2) / 2

            name = names[int(cls)]
            
            if name=="depleeted_cotton_II":
                decision["depleeted_cotton_II"] = True
                decision["depleeted_cotton_II_location"] = (center_x, center_y)
            elif name == "depleeted_cotton_III":
                decision["depleeted_cotton_III"] = True
                decision["depleeted_cotton_III_location"] = (center_x, center_y)
            elif name == "depleeted_cotton_III":
                decision["depleeted_cotton_III"] = True
                decision["depleeted_cotton_III_location"] = (center_x, center_y)
            elif name == "depleeted_cotton_IV":
                decision["depleeted_cotton_IV"] = True
                decision["depleeted_cotton_IV_location"] = (center_x, center_y)
            elif name == "player":
                decision["player"] = True
                decision["player_location"] = (center_x, center_y)
            if name == "cotton_II":
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
            if name == "cotton_III":
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
            if name == "cotton_IV":
                decision["cotton_IV"] = True
                distance = ((center_x - screenx_center) ** 2 + (center_y - screeny_center) **2) **.5
                if "cotton_IV_location" in decision:
                        # Calculate if closer
                    if distance < decision["cotton_IV_distance"]:
                        decision["cotton_IV_location"] = (center_x, center_y)
                        decision["cotton_IV_distance"] = distance
                else:
                    decision["cotton_IV_location"] = (center_x, center_y)
                    decision["cotton_IV_distance"] = distance
        end_time = time.time()
        processing_time = end_time - start_time
        print(f"Image processing time: {processing_time:.2f} seconds")
        
        run_bot(decision, processing_time)

def take_screenshot_mount(stop_event, model):
    screenx_center = 1920/2
    screeny_center = 1080/2
    pyautogui.FAILSAFE = False

    while not stop_event.is_set():
        
        decision_mount = {
    "mount": False,
    }
        start_time = time.time()
        # Take screenshot
        screenshot = pyautogui.screenshot() 
        screenshot = Image.frombytes('RGB', screenshot.size, screenshot.tobytes())
        
        results = model([screenshot], conf=.30)  # return a list of Results objects
        boxes = results[0].boxes.xyxy.tolist()
        classes = results[0].boxes.cls.tolist()
        names = results[0].names
        confidences = results[0].boxes.conf.tolist()

        # Process results list
        for box, cls, conf in zip(boxes, classes, confidences):
            x1, y1, x2, y2 = box
            
            center_x = (x1+x2) / 2
            center_y = (y1+y2) / 2

            name = names[int(cls)]
            if name == "mount":
                decision_mount["mount"] = True
                decision_mount["mount_location"] = (center_x, center_y)
                distance = ((center_x - screenx_center) ** 2 + (center_y - screeny_center) **2) **.5
                decision_mount["mount_distance"] = distance
        end_time = time.time()
        processing_time_mount = end_time - start_time
        print(f"Image processing time: {processing_time_mount:.2f} seconds")
        mount_up(decision_mount, processing_time_mount)
        

# Main function
def main():
    print(pyautogui.KEYBOARD_KEYS)
    model = YOLO('best(1).pt')
    stop_event = threading.Event()
    
    # Create and start the screenshot thread
    screenshot_thread = threading.Thread(target=take_screenshot, args=(stop_event, model))
    screenshot_thread.start()

    # Listen for keyboard input to quit the program
    keyboard.wait("space")

    stop_event.set()

    # Wait for the screenshot thread to finish
    screenshot_thread.join()

    print("Program ended.")

if __name__ == "__main__":
    main()