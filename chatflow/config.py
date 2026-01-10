import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
REF_IMAGE = os.path.join(ASSETS_DIR, "send_icon.png")

DEFAULT_SESSION_DIR = os.path.join(os.getcwd(), "wa_session")

SELECTORS = {
    'search_box': 'div[contenteditable="true"][data-tab="3"]',
    'message_box': 'footer div[contenteditable="true"]',
    'landing_indicator': '#pane-side',
    
    # --- FIXED SELECTOR ---
    # We look for ANY of these to confirm the Image Window opened:
    # 1. The Send Icon (Green button)
    # 2. The "X" Close Button (x-viewer) - Very reliable
    # 3. The Caption Input Container
    # 4. The Media Panel itself
    'media_editor': ', '.join([
        '[data-icon="send"]',
        '[data-icon="x-viewer"]', 
        '[data-testid="media-caption-input-container"]', 
        '[data-testid="media-editor-panel"]',
        '[data-testid="drawer-middle"]'
    ]),
    
    'msg_row': 'div[role="row"]',
    'msg_sent': 'span[data-icon="msg-check"], span[data-icon="msg-dblcheck"]'
}