class ChatFlowError(Exception): pass
class LoginTimeoutError(ChatFlowError): pass
class ChatNotFoundError(ChatFlowError): pass