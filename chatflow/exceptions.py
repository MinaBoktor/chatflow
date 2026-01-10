class ChatFlowError(Exception):
    """Base exception for ChatFlow."""
    pass

class LoginTimeoutError(ChatFlowError):
    """Raised when WhatsApp login takes too long."""
    pass

class ChatNotFoundError(ChatFlowError):
    """Raised when the contact cannot be found."""
    pass

class MessageSendError(ChatFlowError):
    """Raised when the message fails to verify as sent."""
    pass