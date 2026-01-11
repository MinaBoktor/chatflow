import time
import logging
import random
import pyautogui
from playwright.sync_api import sync_playwright
from . import config, utils, exceptions

logging.basicConfig(level=logging.INFO, format='[zajel] %(message)s')
logger = logging.getLogger("zajel")

class Zajel:
    def __init__(self, session_dir=config.DEFAULT_SESSION_DIR, headless=False):
        self.session_dir = session_dir
        self.headless = headless
        
        logger.info(f"Starting zajel (Session: {self.session_dir})")
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

    def send_bulk(self, contacts: list, min_delay=10, max_delay=25):
        total = len(contacts)
        logger.info(f"🚀 Starting Bulk Campaign: {total} messages.")
        for i, contact in enumerate(contacts):
            phone = contact.get('phone')
            msg = contact.get('message', "")
            media = contact.get('media_path', None) # Renamed for clarity, logic is same
            
            logger.info(f"--- Processing [{i+1}/{total}]: {phone} ---")
            self.send_message(phone, msg, media)
            
            if i < total - 1:
                sleep_time = random.randint(min_delay, max_delay)
                logger.info(f"😴 Safety Sleep: Waiting {sleep_time} seconds...")
                time.sleep(sleep_time)
        logger.info("✅ Bulk Campaign Completed!")

    def send_message(self, phone: str, message: str = "", media_path: str = None):
        """
        Sends a message to a phone number.
        :param media_path: Path to ANY file (Image, PDF, Video).
        """
        try:
            self.page.bring_to_front()
            clean_phone = phone.replace("+", "").replace(" ", "")
            
            # --- RESET UI ---
            logger.info("Resetting UI state...")
            self.page.keyboard.press("Escape")
            time.sleep(0.5)
            self.page.keyboard.press("Escape")
            time.sleep(1.0) 
            
            # 1. Search
            logger.info(f"Searching for {clean_phone}...")
            self.page.click(config.SELECTORS['search_box'])
            self.page.keyboard.press("Control+a")
            self.page.keyboard.press("Backspace")
            self.page.keyboard.type(clean_phone)
            time.sleep(3.0) 
            self.page.keyboard.press("Enter")
            
            # 2. Verify Chat Open
            try:
                self.page.wait_for_selector(config.SELECTORS['message_box'], timeout=30000)
            except:
                logger.error(f"❌ Chat failed to load for {clean_phone}")
                self.page.keyboard.press("Escape")
                self.page.keyboard.press("Escape")
                return

            # 3. Media Logic (Universal Copy-Paste)
            if media_path:
                # Use the new Universal File Copy function
                if utils.copy_file_to_clipboard(media_path):
                    logger.info(f"Pasting media: {media_path}...")
                    
                    # Paste Loop
                    paste_success = False
                    for i in range(3):
                        self.page.click(config.SELECTORS['message_box'], force=True)
                        time.sleep(0.2)
                        self.page.keyboard.press("Control+v")
                        time.sleep(1.5) 
                        
                        if utils.find_button_on_monitor(config.REF_SEND_ICON):
                            logger.info("✅ Visual Check: Preview Window Open.")
                            paste_success = True
                            break
                        if self.page.is_visible(config.SELECTORS['media_editor']):
                            paste_success = True
                            break
                    
                    if not paste_success:
                        logger.error("❌ Failed to paste media.")
                        return

                    if message: self.page.keyboard.type(message)
                    
                    # Click Send
                    logger.info("Vision: Clicking Send Button...")
                    coords = utils.find_button_on_monitor(config.REF_SEND_ICON)
                    if coords:
                        utils.human_click(coords[0], coords[1])
                        try:
                            self.page.wait_for_selector(config.SELECTORS['media_editor'], state="hidden", timeout=8000)
                        except:
                            logger.error("❌ Window stuck open.")
                            return
                        
                        self._smart_verify()
                    else:
                        logger.error("❌ Send button not found.")
            else:
                self.page.click(config.SELECTORS['message_box'], force=True)
                self.page.keyboard.type(message)
                time.sleep(0.5) 
                self.page.keyboard.press("Enter")
                self._smart_verify()
                
        except Exception as e:
            logger.error(f"Error: {e}")

    def _smart_verify(self):
        logger.info("Verifying delivery...")
        start_time = time.time()
        timeout = 10 
        while time.time() - start_time < timeout:
            try:
                last_msg = self.page.locator(config.SELECTORS['msg_row']).last
                if last_msg.locator(config.SELECTORS['msg_sent']).is_visible():
                    logger.info("✅ SUCCESS: Tick found immediately.")
                    return
            except: pass
            
            clock_box = utils.find_latest_clock(config.REF_CLOCK)
            if clock_box:
                logger.info(f"🕒 Clock detected at {clock_box}. Locking on...")
                changed = utils.wait_for_pixel_change(clock_box, timeout=30)
                if changed:
                    logger.info("✅ SUCCESS: Clock turned into Tick.")
                else:
                    logger.error("❌ FAILED: Message stuck on Clock for 30s.")
                return
            time.sleep(0.5)
        logger.error("❌ FAILED: Timed out. Neither Clock nor Tick appeared.")

    def close(self, keep_open=False):
        if keep_open: 
            logger.info("⏸️ Browser kept open. Press ENTER to close...")
            input()
        if self.browser: self.browser.close()
        if self.playwright: self.playwright.stop()