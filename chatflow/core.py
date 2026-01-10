import os
import time
import logging
from playwright.sync_api import sync_playwright
from . import config, utils, vision, exceptions

logging.basicConfig(level=logging.INFO, format='[ChatFlow] %(message)s')
logger = logging.getLogger("ChatFlow")

class ChatFlow:
    def __init__(self, session_dir=config.DEFAULT_SESSION_DIR, headless=False):
        self.session_dir = session_dir
        self.headless = headless
        
        logger.info(f"Starting ChatFlow (Session: {self.session_dir})")
        self.playwright = sync_playwright().start()
        
        # Launch Browser
        self.browser = self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.session_dir,
            headless=self.headless,
            args=["--start-maximized"],
            no_viewport=True,
            permissions=["clipboard-read", "clipboard-write"]
        )
        
        # Get or create page
        self.page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()
        self.page.goto("https://web.whatsapp.com/")
        
        try:
            logger.info("Waiting for login...")
            self.page.wait_for_selector(config.SELECTORS['landing_indicator'], timeout=60000)
            logger.info("✅ Login Successful")
        except:
            raise exceptions.LoginTimeoutError("Login Failed or Timed Out")

    def send_message(self, phone: str, message: str = "", image_path: str = None):
        try:
            self.page.bring_to_front()
            clean_phone = phone.replace("+", "").replace(" ", "")
            
            # 1. Search
            logger.info(f"Searching for {clean_phone}...")
            self.page.click(config.SELECTORS['search_box'])
            
            # CLEAR EXISTING TEXT (Critical Fix)
            self.page.keyboard.press("Control+a")
            self.page.keyboard.press("Backspace")
            
            self.page.keyboard.type(clean_phone)
            time.sleep(1.5) 
            self.page.keyboard.press("Enter")
            
            # 2. Verify Open
            try:
                self.page.wait_for_selector(config.SELECTORS['message_box'], timeout=5000)
            except:
                logger.error(f"❌ Chat not found for {clean_phone}")
                return

            # 3. Send Logic
            if image_path:
                if utils.copy_image_to_clipboard(image_path):
                    logger.info("Pasting image...")
                    self.page.click(config.SELECTORS['message_box'])
                    time.sleep(0.5)
                    self.page.keyboard.press("Control+v")
                    
                    # --- THE FIX IS HERE ---
                    # We now call 'smart_send_and_verify', not 'click_and_verify'
                    sent = vision.smart_send_and_verify(
                        self.page, 
                        config.SELECTORS['preview_send_button']
                    )
                    
                    if sent:
                        logger.info("✅ Image Sent")
                        if message:
                             # If you want to send the caption as text after:
                             # self.page.keyboard.type(message)
                             # self.page.keyboard.press("Enter")
                             pass
                    else:
                        logger.error("❌ Failed to verify send")

            else:
                self.page.click(config.SELECTORS['message_box'])
                self.page.keyboard.type(message)
                self.page.keyboard.press("Enter")
                logger.info("✅ Text Sent")
                
        except Exception as e:
            logger.error(f"Error: {e}")

    def close(self):
        self.browser.close()
        self.playwright.stop()