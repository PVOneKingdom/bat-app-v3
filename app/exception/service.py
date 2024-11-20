class MismatchedIds(Exception):
    def __init__(self, msg: str):
        self.msg = msg

class InvalidConstantValue(Exception):
    def __init__(self, msg: str):
        self.msg = msg

class IncorectCredentials(Exception):
    def __init__(self, msg: str):
        self.msg = msg

class InvalidBearerToken(Exception):
    def __init__(self, msg: str):
        self.msg = msg

class Unauthorized(Exception):
    def __init__(self, msg: str):
        self.msg = msg

class EndpointDataMismatch(Exception):
    def __init__(self, msg: str):
        self.msg = msg

class InvalidNewOrderData(Exception):
    def __init__(self, msg: str):
        self.msg = msg
