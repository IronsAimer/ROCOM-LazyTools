##################### N I G H T M A T E #####################
# Brief:
#  An automation tool to control your nightmare mate to:
#   - Apply the first skill to the nightmare in the battle.
#   - Recovery energy in the phase of waiting for capture.
#   - Or other keyboard actions using pydirectinput.
#
# Usage:
#  To prepare:
#   "pip install -r requirements.txt"
#   - If you do not have pytorch, easyocr will install the
#     CPU version by default.
#  To run :
#   "python nightmate.py"
#   - Admin permission is required to use pydirectinput.
#   
# Last updated: 2026-04-09 20:07
# File: nightmate.py
#############################################################

#### W A R N I N G #### W A R N I N G #### W A R N I N G ####
#
# ! This tool is for educational purposes only. Please use 
#   it responsibly and at your own risk. The author is not
#   liable for any damage or loss caused by using this tool.
#
# ! The code is free and open-source on GitHub. If you payed
#   for using, you may have been scammed and you could get
#   the code for free on the link above.
#
# ! This tool is not so stable for many reasons including:
#   - the accuracy of OCR (affecting the status update)
#   - the performance of hardwares (it is suggested to run
#     the code with pytorch CUDA version. Using CPU for OCR
#     may cause important input delay, which easily leads to
#     a longer PRESS_DURATION than settings)
#
#### W A R N I N G #### W A R N I N G #### W A R N I N G ####

import tkinter as tk
import pyautogui
import pydirectinput
import easyocr
import numpy as np
import time
from PIL import Image, ImageOps
import re

LONG_SLEEP = 1.0
SHORT_SLEEP = 0.1
PRESS_DURATION = 0.05

class RegionSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Please select the region to monitor, ESC to cancel")
        self.root.attributes('-alpha', 0.3)
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.canvas = tk.Canvas(self.root, cursor="cross", bg="grey")
        self.canvas.pack(fill="both", expand=True)
        
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.selection = None

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='red', width=2)

    def on_move_press(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        left, top = min(self.start_x, event.x), min(self.start_y, event.y)
        width, height = abs(event.x - self.start_x), abs(event.y - self.start_y)
        self.selection = (left, top, width, height)
        self.root.destroy()

    def get_selection(self):
        self.root.mainloop()
        return self.selection

def readPercentage(reader, region) -> int:
    """
    EasyOCR used to read the percentage value from a screenshot of the region selected.
    
    Returns:
        int: the percentage value, -1 if nothing matched.
    """
    screenshot = pyautogui.screenshot(region=region)
    gray_image = screenshot.convert('L')
    processed_image = ImageOps.autocontrast(gray_image, cutoff=0.5)
    img_np = np.array(screenshot)

    # only recognize digits and %
    results = reader.readtext(img_np, detail=0, allowlist='0123456789%')
    full_text = "".join(results).replace(" ", "").replace("O", "0")
    
    match = re.search(r"(\d+)%", full_text)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return -1
    return -1

def attack():
    pydirectinput.keyDown('1')
    time.sleep(PRESS_DURATION)
    pydirectinput.keyUp('1')

def energy():
    pydirectinput.keyDown('x')
    time.sleep(PRESS_DURATION)
    pydirectinput.keyUp('x')

# another example of keybord input
def catch():
    pydirectinput.keyDown('w')
    time.sleep(PRESS_DURATION)
    pydirectinput.keyUp('w')

    time.sleep(10 * PRESS_DURATION)

    pydirectinput.keyDown('1')
    time.sleep(PRESS_DURATION)
    pydirectinput.keyUp('1')

    time.sleep(10 * PRESS_DURATION)

    pydirectinput.keyDown('space')
    time.sleep(PRESS_DURATION)
    pydirectinput.keyUp('space')

def monitor(region):
    print("Loading EasyOCR model...")
    reader = easyocr.Reader(['en']) 
    
    left, top, width, height = region
    print(f"Monitoring starts in region: {region}\n")

    status = -1 # -1=initialized, 0=invalid state, 1=new nightmare, 2=waiting capture, 3=unknown
    last_r = -1
    while True:        
        time.sleep(SHORT_SLEEP)

        # OCR 
        r = readPercentage(reader, region)
        if r == last_r and status == 0:
            continue
        last_r = r

        # status update
        if r == -1:
            print(f"[{time.strftime('%H:%M:%S')}] OCR found {r}% \t -> Invalid value, going to the next loop.")
            status = 0
            continue
        if status == 0 and r == 100:
            print(f"[{time.strftime('%H:%M:%S')}] OCR found {r}% \t -> New nightmare detected.")
            status = 1
        elif status == 1 and r == 0:
            print(f"[{time.strftime('%H:%M:%S')}] OCR found {r}% \t -> Will verify if health of the nightmare is restored to 10%")
            status = 3
            continue
        elif status == 3 and r == 10:
            print(f"[{time.strftime('%H:%M:%S')}] OCR found {r}% \t -> Defeated nightmare, waiting for capture")
            status = 2
        elif status == -1 and r > 0 and r < 100:
            status = 1
        elif status == 0 and r > 0 and r < 100:
            status = 2
        
        # actions based on status
        if status == 1:
            print(f"[{time.strftime('%H:%M:%S')}] OCR found {r}% \t -> Fighting against nightmare, will use default attack key 1")
            time.sleep(LONG_SLEEP)
            attack()
        if status == 2:
            print(f"[{time.strftime('%H:%M:%S')}] OCR found {r}% \t -> Waiting for capture, will use default energy key X")
            time.sleep(LONG_SLEEP)
            catch()


if __name__ == "__main__":
    selector = RegionSelector()
    area = selector.get_selection()

    if area and area[2] > 0:
        try:
            monitor(area)
        except KeyboardInterrupt:
            print("\nProgram manually stopped.")
    else:
        print("No valid region selected. Exiting.")