import mss
import keyboard
import time

keyboard.wait('space')
image_counter = 0

while not keyboard.is_pressed('p'):
    with mss.mss() as sct:
        filename = sct.shot(mon=1 , output=f".\ImageData\ALBION_BOT-{image_counter}.png")
        print(filename)
        image_counter += 1
        time.sleep(7 )   