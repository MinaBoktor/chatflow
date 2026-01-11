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
            except:
                logger.error(f"❌ Chat not found for {clean_phone}")
                return

            # 3. Send Logic
            if image_path:
                if utils.copy_image_to_clipboard(image_path):
                    logger.info("Pasting image...")
                    
                    # Paste Loop
                    paste_success = False
                    for i in range(3):
                        self.page.click(config.SELECTORS['message_box'], force=True)
                        time.sleep(0.2)
                        self.page.keyboard.press("Control+v")
                        time.sleep(1.5) 
                        
                        if utils.find_button_on_monitor(config.REF_SEND_ICON):
                            logger.info("✅ Visual Check: Window Open.")
                            paste_success = True
                            break
                        if self.page.is_visible(config.SELECTORS['media_editor']):
                            paste_success = True
                            break
                    
                    if not paste_success:
                        logger.error("❌ Failed to open image window.")
                        return

                    if message: self.page.keyboard.type(message)
                    
                    # Click Send
                    logger.info("Vision: Clicking Send Button...")
                    coords = utils.find_button_on_monitor(config.REF_SEND_ICON)
                    if coords:
                        utils.human_click(coords[0], coords[1])
                        # Wait for window close
                        try:
                            self.page.wait_for_selector(config.SELECTORS['media_editor'], state="hidden", timeout=8000)
                        except:
                            logger.error("❌ Window stuck open.")
                            return
                        
                        # Verify Delivery (Polling Strategy)
                        self._smart_verify()
                    else:
                        logger.error("❌ Send button not found.")
            else:
                self.page.click(config.SELECTORS['message_box'], force=True)
                self.page.keyboard.type(message)
                self.page.keyboard.press("Enter")
                self._smart_verify()
                
        except Exception as e:
            logger.error(f"Error: {e}")

    def _smart_verify(self):
        """
        Polls for 10 seconds looking for EITHER:
        1. A Clock (to start monitoring).
        2. A Tick (to confirm instant success).
        """
        logger.info("Verifying delivery (Polling for Status)...")
        
        start_time = time.time()
        timeout = 10  # Seconds to find the initial status
        
        while time.time() - start_time < timeout:
            
            # A. Check for Immediate Success (Tick) via DOM
            # This handles "Instant Send" where Clock never appears
            try:
                last_msg = self.page.locator(config.SELECTORS['msg_row']).last
                if last_msg.locator(config.SELECTORS['msg_sent']).is_visible():
                    logger.info("✅ SUCCESS: Tick found immediately.")
                    return
            except:
                pass

            # B. Check for Pending State (Clock) via Vision
            # This handles "Slow Send"
            clock_box = utils.find_latest_clock(config.REF_CLOCK)
            if clock_box:
                logger.info(f"🕒 Clock detected at {clock_box}. Locking on...")
                
                # We found the clock! Now we wait up to 30s for it to change.
                changed = utils.wait_for_pixel_change(clock_box, timeout=30)
                if changed:
                    logger.info("✅ SUCCESS: Clock turned into Tick.")
                else:
                    logger.error("❌ FAILED: Message stuck on Clock for 30s.")
                return

            # Wait briefly before scanning again to save CPU
            time.sleep(0.5)

        logger.error("❌ FAILED: Timed out. Neither Clock nor Tick appeared.")

    def close(self, keep_open=False):
        if keep_open: 
            logger.info("⏸️ Browser kept open. Press ENTER to close...")
            input()
        if self.browser: self.browser.close()
        if self.playwright: self.playwright.stop()