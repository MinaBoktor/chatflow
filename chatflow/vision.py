import time
import logging
import pyautogui
from playwright.sync_api import Page
from . import config, utils

logger = logging.getLogger("ChatFlow")

def smart_send_and_verify(page: Page, click_selector: str) -> bool:
    """
    1. Click (DOM or Vision).
    2. Verify by waiting for the 'Single Tick' (msg-check) to appear.
    """
    
    # --- STEP 1: PERFORM THE CLICK ---
    clicked = False
    
    # Attempt A: DOM Click
    try:
        if page.is_visible(click_selector):
            page.click(click_selector)
            clicked = True
            logger.info("DOM: Clicked Send Button.")
    except:
        pass

    # Attempt B: Vision Click (Fallback)
    if not clicked:
        logger.info("DOM element not found. Trying Vision...")
        fallback_images = [config.REF_LIGHT, config.REF_DARK]
        for img_path in fallback_images:
            coords = utils.find_button_on_screen(img_path)
            if coords:
                pyautogui.moveTo(coords[0], coords[1])
                pyautogui.click()
                pyautogui.moveTo(10, 10) # Un-hover
                logger.info(f"Vision: Clicked button at {coords}.")
                clicked = True
                break
    
    if not clicked:
        # Final fallback: Just hit Enter and hope
        logger.warning("Could not click button. Attempting Enter key...")
        page.keyboard.press("Enter")

    # --- STEP 2: VERIFY (THE TICK CHECK) ---
    # We wait for the 'Single Tick' to appear. 
    # This confirms the message reached the WhatsApp Server.
    try:
        # We wait up to 10 seconds for the tick.
        # This handles slow internet automatically.
        page.wait_for_selector(config.SELECTORS['msg_sent'], timeout=10000)
        logger.info("✅ Verification: Single Tick detected. Message Sent.")
        return True
    except:
        logger.error("❌ Verification Failed: No tick appeared (Message not sent).")
        return False