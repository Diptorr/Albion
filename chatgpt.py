import threading
import pyautogui
import keyboard
from PIL import Image
from ultralytics import YOLO
import time
from PIL import ImageGrab
import random

# Initialize YOLO model
model = YOLO('best(1).pt')

# Initialize threading event
stop_event = threading.Event()

# Initialize timestamp for last click
last_click_time = 0

# Function to check if a pixel is green
def is_green(pixel):
    green_min = (0, 100, 0)  # Minimum RGB values for green
    green_max = (50, 255, 50)  # Maximum RGB values for green
    return all(green_min[i] <= pixel[i] <= green_max[i] for i in range(3))

# Function to find all green pixels on the screen
def find_green_pixels():
    green_pixels = []
    screen = ImageGrab.grab()
    width, height = screen.size
    for x in range(width):
        for y in range(height):
            pixel = screen.getpixel((x, y))
            if is_green(pixel):
                green_pixels.append((x, y))
    return green_pixels

# Function to handle mount actions
def mount_up(decision_mount):
    global last_click_time
    if decision_mount["mount"]:
        pyautogui.click(decision_mount["mount_location"])
        last_click_time = time.time()
        print("Going to mount:", decision_mount["mount_location"])
    else:
        pyautogui.press('a')
        last_click_time = time.time()
    take_screenshot(stop_event, model)

# Function to handle bot actions
def run_bot(decision):
    global last_click_time
    cotton_types = ["cotton_II", "cotton_III", "cotton_IV"]
    for cotton_type in cotton_types:
        if decision[cotton_type]:
            pyautogui.click(decision[cotton_type + "_location"])
            last_click_time = time.time()
            print(f"Going to {cotton_type}:", decision[cotton_type + "_location"])
            take_screenshot_mount(stop_event, model)
            return
    green_pixels = find_green_pixels()
    if green_pixels and time.time() - last_click_time > 3:  # Throttle clicking
        random_green_pixel = random.choice(green_pixels)
        print(f"Clicking on random green pixel at {random_green_pixel}")
        pyautogui.click(random_green_pixel)
        last_click_time = time.time()
    else:
        print("No cotton or green pixel found. Clicking at default location.")
        pyautogui.press('a')
        last_click_time = time.time()
        pyautogui.click(500, 700)

# Function to take screenshots
# Function to take screenshots
def take_screenshot(stop_event, model):
    while not stop_event.is_set():
        decision = {
            "cotton_II": False,
            "cotton_III": False,
            "cotton_IV": False,
            "player": False,
            "depleted_cotton_II": False,
            "depleted_cotton_III": False,
            "depleted_cotton_IV": False,
        }
        start_time = time.time()
        screenshot = pyautogui.screenshot(region=(100, 100, 800, 800))
        screenshot = Image.frombytes('RGB', screenshot.size, screenshot.tobytes())
        results = model([screenshot], conf=0.60)
        
        for pred in results.pred[0]:
            box = pred[:4]
            cls = pred[5]
            conf = pred[4]
            
            x1, y1, x2, y2 = box
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            name = results.names[cls]
            
            if name.startswith("depleted_cotton"):
                decision[name] = True
                decision[name + "_location"] = (center_x, center_y)
            elif name in ["cotton_II", "cotton_III", "cotton_IV"]:
                decision[name] = True
                cotton_type = name
                distance = ((center_x - 960) ** 2 + (center_y - 540) ** 2) ** 0.5  # Assuming screen resolution is 1920x1080
                if cotton_type + "_location" in decision:
                    if distance < decision[cotton_type + "_distance"]:
                        decision[cotton_type + "_location"] = (center_x, center_y)
                        decision[cotton_type + "_distance"] = distance
                else:
                    decision[cotton_type + "_location"] = (center_x, center_y)
                    decision[cotton_type + "_distance"] = distance
        
        end_time = time.time()
        processing_time = end_time - start_time
        print(f"Image processing time: {processing_time:.2f} seconds")
        run_bot(decision)

# Function to take mount screenshots
def take_screenshot_mount(stop_event, model):
    while not stop_event.is_set():
        decision_mount = {"mount": False}
        start_time = time.time()
        screenshot = pyautogui.screenshot(region=(860, 390, 200, 300)) 
        screenshot = Image.frombytes('RGB', screenshot.size, screenshot.tobytes())
        results = model([screenshot], conf=0.30)
        boxes = results.xyxy[0].tolist()
        classes = results.names[results.xyxy[0].cls.tolist()]
        confidences = results.xyxy[0].conf.tolist()
        for box, cls, conf in zip(boxes, classes, confidences):
            x1, y1, x2, y2 = box
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            name = cls
            if name == "mount":
                decision_mount["mount"] = True
                decision_mount["mount_location"] = (center_x, center_y)
                distance = ((center_x - 960) ** 2 + (center_y - 540) ** 2) ** 0.5  # Assuming screen resolution is 1920x1080
                decision_mount["mount_distance"] = distance
        end_time = time.time()
        processing_time_mount = end_time - start_time
        print(f"Image processing time: {processing_time_mount:.2f} seconds")
        mount_up(decision_mount)

# Main function
def main():
    print(pyautogui.KEYBOARD_KEYS)
    global last_click_time
    last_click_time = time.time()
    stop_event = threading.Event()
    screenshot_thread = threading.Thread(target=take_screenshot, args=(stop_event, model))
    screenshot_thread.start()
    keyboard.wait("space")
    stop_event.set()
    screenshot_thread.join()
    print("Program ended.")

if __name__ == "__main__":
    main()
