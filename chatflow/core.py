import time
import logging
import pyautogui
from playwright.sync_api import sync_playwright
from . import config, utils, exceptions

logging.basicConfig(level=logging.INFO, format='[ChatFlow] %(message)s')
logger = logging.getLogger("ChatFlow")

class ChatFlow:
    def __init__(self, session_dir=config.DEFAULT_SESSION_DIR, headless=False):
        self.session_dir = session_dir
        self.headless = headless
        
        logger.info(f"Starting ChatFlow (Session: {self.session_dir})")
        self.playwright = sync_playwright().start()
        
        self.browser = self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.session_dir,
            headless=self.headless,
            args=["--start-maximized"],
            no_viewport=True,
            permissions=["clipboard-read", "clipboard-write"]
        )
        
        self.page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()
        self.page.goto("https://web.whatsapp.com/")
        
        try:
            logger.info("Waiting for login...")
            self.page.wait_for_selector(config.SELECTORS['landing_indicator'], timeout=60000)
            logger.info("✅ Login Successful")
        except:
            raise exceptions.LoginTimeoutError("Login timed out.")

    def send_message(self, phone: str, message: str = "", image_path: str = None):
        try:
            self.page.bring_to_front()
            clean_phone = phone.replace("+", "").replace(" ", "")
            
            # 1. Search
            logger.info(f"Searching for {clean_phone}...")
            self.page.click(config.SELECTORS['search_box'])
            self.page.keyboard.press("Control+a")
            self.page.keyboard.press("Backspace")
            self.page.keyboard.type(clean_phone)
            time.sleep(1.5)
            self.page.keyboard.press("Enter")
            
            # 2. Verify Chat Open
            try:
                self.page.wait_for_selector(config.SELECTORS['message_box'], timeout=5000)
                pre_count = self.page.locator(config.SELECTORS['msg_row']).count()
            except:
                logger.error(f"❌ Chat not found for {clean_phone}")
                return

            # 3. Send Logic
            if image_path:
                if utils.copy_image_to_clipboard(image_path):
                    logger.info("Pasting image...")
                    
                    paste_success = False
                    for i in range(3):
                        # Check if window is ALREADY open (e.g. from previous loop)
                        if self.page.is_visible(config.SELECTORS['media_editor']):
                            logger.info("✅ Image Window detected (Already Open).")
                            paste_success = True
                            break

                        try:
                            # A. Force Focus
                            self.page.click(config.SELECTORS['message_box'], force=True)
                            time.sleep(0.2)
                            self.page.keyboard.press("Space") 
                            self.page.keyboard.press("Backspace")
                            
                            # B. Paste
                            time.sleep(0.5)
                            self.page.keyboard.press("Control+v")
                            
                            # C. Check for Modal (Increased Timeout to 5s)
                            self.page.wait_for_selector(config.SELECTORS['media_editor'], timeout=5000)
                            logger.info("✅ Image Window detected.")
                            paste_success = True
                            break 
                        except Exception:
                            logger.warning(f"⚠️ Paste attempt {i+1} failed to detect window. Retrying...")
                            time.sleep(1)
                    
                    if not paste_success:
                        logger.error("❌ Paste failed: Image preview window didn't open.")
                        return

                    # D. Type Caption
                    if message:
                        self.page.keyboard.type(message)
                    
                    # E. Physical Click (Human Style)
                    logger.info("Vision: Scanning for Send Button...")
                    coords = utils.find_button_on_monitor(config.REF_IMAGE)
                    
                    if coords:
                        logger.info(f"Vision: Found at {coords}. Clicking human-style...")
                        utils.human_click(coords[0], coords[1])
                    else:
                        logger.warning("Vision: Button not found. Trying Enter key.")
                        self.page.keyboard.press("Enter")
                    
                    # F. Verify (Strict)
                    try:
                        self.page.wait_for_selector(config.SELECTORS['media_editor'], state="hidden", timeout=8000)
                        logger.info("✅ UI Verification: Preview window closed.")
                    except:
                        logger.error("❌ FAILED: Image preview window stuck open. Click missed.")
                        return 
                    
                    self._verify_tick(pre_count)

            else:
                self.page.click(config.SELECTORS['message_box'], force=True)
                self.page.keyboard.type(message)
                self.page.keyboard.press("Enter")
                self._verify_tick(pre_count)
                
        except Exception as e:
            logger.error(f"Error: {e}")

    def _verify_tick(self, pre_count):
        logger.info("Verifying delivery on server...")
        try:
            new_msg_appeared = False
            for _ in range(20): 
                curr = self.page.locator(config.SELECTORS['msg_row']).count()
                if curr > pre_count:
                    new_msg_appeared = True
                    break
                time.sleep(0.5)
            
            if not new_msg_appeared:
                logger.error("❌ FAILED: Message count did not increase.")
                return

            last_msg = self.page.locator(config.SELECTORS['msg_row']).last
            last_msg.locator(config.SELECTORS['msg_sent']).wait_for(state="visible", timeout=10000)
            logger.info("✅ SUCCESS: Tick verified.")
        except:
            logger.error("❌ FAILED: Tick verification timed out.")

    def close(self):
        self.browser.close()
        self.playwright.stop()