class ZajelError(Exception): pass
class LoginTimeoutError(ZajelError): pass
class ChatNotFoundError(ZajelError): pass