import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

REF_SEND_ICON = os.path.join(ASSETS_DIR, "send_icon.png")
# NEW: The Clock Icon (Pending State)
REF_CLOCK = os.path.join(ASSETS_DIR, "clock_icon.png")

DEFAULT_SESSION_DIR = os.path.join(os.getcwd(), "wa_session")

SELECTORS = {
    'search_box': 'div[contenteditable="true"][data-tab="3"]',
    'message_box': 'footer div[contenteditable="true"]',
    'landing_indicator': '#pane-side',
    
    # Media signals
    'media_editor': ', '.join([
        '[data-icon="send"]',
        '[data-icon="x-viewer"]', 
        '[data-testid="media-caption-input-container"]', 
        '[data-testid="media-editor-panel"]',
        '[data-testid="drawer-middle"]'
    ]),
    
    'msg_row': 'div[role="row"]'
}