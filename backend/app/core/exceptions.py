class AuthenticationError(Exception):
    def __init__(self, detail: str = 'Authentication failed') -> None:
        self.detail = detail
        super().__init__(detail)


class AuthorizationError(Exception):
    def __init__(self, detail: str = 'Not authorized to access this resource') -> None:
        self.detail = detail
        super().__init__(detail)


class ConfigurationError(Exception):
    def __init__(self, detail: str = 'Server authentication configuration is invalid') -> None:
        self.detail = detail
        super().__init__(detail)


class ValidationError(Exception):
    def __init__(self, detail: str = 'The request payload is invalid') -> None:
        self.detail = detail
        super().__init__(detail)


class ProcessingError(Exception):
    def __init__(self, detail: str = 'Unable to process the requested resource') -> None:
        self.detail = detail
        super().__init__(detail)
