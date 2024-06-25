class EmailNotValid(Exception):
    def __init__(self, message="email not active"):
        self.message = message
        super().__init__(self.message)


class PasswordNotSecure(Exception):
    def __init__(self, message="password not secure"):
        self.message = message
        super().__init__(self.message)


class UserNotFound(Exception):
    def __init__(self, message="user not found"):
        self.message = message
        super().__init__(self.message)


class ShortURLNotFound(Exception):
    def __init__(self, message="short url not found"):
        self.message = message
        super().__init__(self.message)


class ShortURLNotAvaible(Exception):
    def __init__(self, message="short url not avaible"):
        self.message = message
        super().__init__(self.message)


class EmailAlreadySend(Exception):
    def __init__(self, message="email already active"):
        self.message = message
        super().__init__(self.message)
