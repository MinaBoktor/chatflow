import os
import cv2
import numpy as np
import pyautogui
import win32clipboard
from io import BytesIO
from PIL import Image

def copy_image_to_clipboard(image_path: str) -> bool:
    """Loads image to Windows Clipboard."""
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

def find_button_on_screen(template_path: str):
    """
    Scans the screen for the template image.
    Returns (x, y) center coordinates or None.
    """
    if not os.path.exists(template_path): 
        return None

    # 1. Take Screenshot
    screenshot = pyautogui.screenshot()
    screen_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    screen_gray = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)
    
    # 2. Load Template
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        return None
    th, tw = template.shape[:2]
    
    # 3. Region of Interest (Bottom 50% of screen)
    h, w = screen_gray.shape
    roi_y = int(h * 0.5)
    roi = screen_gray[roi_y:h, 0:w]
    
    found = None
    
    # 4. Multi-Scale Search
    for scale in np.linspace(0.8, 1.2, 10)[::-1]:
        rw, rh = int(tw * scale), int(th * scale)
        if rw > w or rh > roi.shape[0]: continue
        
        resized_template = cv2.resize(template, (rw, rh))
        res = cv2.matchTemplate(roi, resized_template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        
        if max_val > 0.8:
            found = (max_loc, rw, rh)
            break
            
    if found:
        loc, rw, rh = found
        # Calculate global X, Y
        center_x = loc[0] + rw // 2
        center_y = roi_y + loc[1] + rh // 2
        return (center_x, center_y)
        
    return None