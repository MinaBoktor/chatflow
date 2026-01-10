import os
import cv2
import numpy as np
import pyautogui
import win32clipboard
from io import BytesIO
from PIL import Image
import time

# SAFEGUARD: Fail-safe to stop mouse if it goes to corner (0,0)
pyautogui.FAILSAFE = True

def copy_image_to_clipboard(image_path: str) -> bool:
    if not os.path.exists(image_path): return False
    try:
        image = Image.open(image_path)
        output = BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:] 
        output.close()
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
        return True
    except: return False

def find_button_on_monitor(template_path: str):
    """
    Scans the ENTIRE monitor width (Bottom 50%) to support Arabic/English.
    Returns (x, y) or None.
    """
    if not os.path.exists(template_path): return None

    # Take screenshot
    screenshot = pyautogui.screenshot()
    screen_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    # ROI: Bottom 50%, Full Width
    h, w = screen_img.shape[:2]
    roi_y = int(h * 0.50)
    roi_x = 0 
    
    roi_img = screen_img[roi_y:h, roi_x:w]
    roi_gray = cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)
    
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None: return None
    th, tw = template.shape[:2]
    
    found = None
    
    # Multi-Scale Scan
    for scale in np.linspace(0.8, 1.2, 10)[::-1]:
        rw, rh = int(tw * scale), int(th * scale)
        if rw > w or rh > roi_img.shape[0]: continue
        
        resized_template = cv2.resize(template, (rw, rh))
        res = cv2.matchTemplate(roi_gray, resized_template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        
        # High Confidence (0.9)
        if max_val > 0.9:
            found = (max_loc, rw, rh)
            break
            
    if found:
        loc, rw, rh = found
        center_x = roi_x + loc[0] + rw // 2
        center_y = roi_y + loc[1] + rh // 2
        return (center_x, center_y)
        
    return None

def human_click(x, y):
    """Moves mouse slowly and performs a robust click."""
    # 1. Move slowly (0.8 seconds)
    pyautogui.moveTo(x, y, duration=0.8, tween=pyautogui.easeInOutQuad)
    
    # 2. Press down
    pyautogui.mouseDown()
    time.sleep(0.1) # Short hold
    # 3. Release
    pyautogui.mouseUp()
    
    # 4. Move away to un-hover
    pyautogui.moveTo(10, 10, duration=0.2)