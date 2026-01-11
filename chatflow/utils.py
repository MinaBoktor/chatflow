import os
import cv2
import numpy as np
import pyautogui
import win32clipboard
from io import BytesIO
from PIL import Image
import time

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
    """Finds the BEST single match using Multi-Scale."""
    if not os.path.exists(template_path): return None
    
    screenshot = pyautogui.screenshot()
    screen_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    screen_gray = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)
    
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None: return None
    
    h, w = screen_gray.shape
    roi = screen_gray[int(h*0.5):h, 0:w] # Bottom 50%
    th, tw = template.shape[:2]
    
    found = None
    
    for scale in np.linspace(0.8, 1.2, 10)[::-1]:
        rw, rh = int(tw * scale), int(th * scale)
        if rw > w or rh > roi.shape[0]: continue
        
        resized_template = cv2.resize(template, (rw, rh))
        res = cv2.matchTemplate(roi, resized_template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        
        if max_val > 0.9:
            found = (max_loc, rw, rh)
            break
            
    if found:
        loc, rw, rh = found
        # FIX: Convert numpy types to python int
        center_x = int(loc[0] + rw // 2)
        center_y = int(int(h*0.5) + loc[1] + rh // 2)
        return (center_x, center_y)
    return None

def find_latest_clock(template_path: str):
    """
    Finds the BOTTOM-MOST 'Clock' using Multi-Scale.
    Returns standard python ints: (x, y, w, h).
    """
    if not os.path.exists(template_path): 
        print(f"❌ Error: {template_path} not found.")
        return None
    
    screenshot = pyautogui.screenshot()
    screen_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    screen_gray = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)
    
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None: return None
    th, tw = template.shape[:2]
    
    best_match = None
    best_y = -1
    
    for scale in np.linspace(0.8, 1.2, 10)[::-1]:
        rw, rh = int(tw * scale), int(th * scale)
        if rw > screen_gray.shape[1] or rh > screen_gray.shape[0]: continue
        
        resized_template = cv2.resize(template, (rw, rh))
        res = cv2.matchTemplate(screen_gray, resized_template, cv2.TM_CCOEFF_NORMED)
        
        locs = np.where(res >= 0.85)
        
        if len(locs[0]) > 0:
            current_max_idx = np.argmax(locs[0])
            current_y = locs[0][current_max_idx]
            current_x = locs[1][current_max_idx]
            
            if current_y > best_y:
                best_y = current_y
                # FIX: Explicit int() casting
                best_match = (int(current_x), int(current_y), int(rw), int(rh))
                
    return best_match

def wait_for_pixel_change(region, timeout=30):
    """Monitors region for pixel changes."""
    # Ensure all inputs are standard ints
    x, y, w, h = map(int, region)
    
    sw, sh = pyautogui.size()
    if x+w > sw or y+h > sh: return False
    
    start_time = time.time()
    
    # Baseline
    initial_shot = pyautogui.screenshot(region=(x, y, w, h))
    initial_arr = cv2.cvtColor(np.array(initial_shot), cv2.COLOR_RGB2GRAY)
    
    print(f"[Vision] Monitoring region {region} for changes...")
    
    while time.time() - start_time < timeout:
        current_shot = pyautogui.screenshot(region=(x, y, w, h))
        current_arr = cv2.cvtColor(np.array(current_shot), cv2.COLOR_RGB2GRAY)
        
        diff = cv2.absdiff(initial_arr, current_arr)
        non_zero_count = np.count_nonzero(diff)
        
        # Sensitivity: If >10% of pixels change
        if non_zero_count > (w * h) * 0.10:
            return True
            
        time.sleep(0.1) 
        
    return False

def human_click(x, y):
    pyautogui.moveTo(x, y, duration=0.6, tween=pyautogui.easeInOutQuad)
    pyautogui.click()
    pyautogui.moveTo(10, 10, duration=0.2)