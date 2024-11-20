class RecordNotFound(Exception):

    def __init__(self, msg: str):
        self.msg = msg


class UsernameOrEmailNotUnique(Exception):

    def __init__(self, msg: str):
        self.msg = msg

class IntegrityErrorException(Exception):

    def __init__(self, msg: str):
        self.msg = msg
