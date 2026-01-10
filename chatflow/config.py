import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

REF_LIGHT = os.path.join(ASSETS_DIR, "send_light.png")
REF_DARK = os.path.join(ASSETS_DIR, "send_dark.png")
DEFAULT_SESSION_DIR = os.path.join(os.getcwd(), "wa_session")

SELECTORS = {
    'search_box': 'div[contenteditable="true"][data-tab="3"]',
    'message_box': 'footer div[contenteditable="true"]',
    'preview_send_button': '[data-icon="send"]',
    'landing_indicator': '#pane-side',
    
    # --- NEW: VERIFICATION SELECTOR ---
    # We look for the "Single Tick" (Sent) OR "Double Tick" (Delivered)
    # This selector targets ANY message with these icons.
    # Since we just sent a message, a new one appearing at the bottom triggers this.
    'msg_sent': 'span[data-icon="msg-check"], span[data-icon="msg-dblcheck"]'
}

TIMEOUT_LOGIN = 60
TIMEOUT_SEND = 15