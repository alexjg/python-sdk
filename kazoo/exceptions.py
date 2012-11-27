
class InvalidConfigurationError(RuntimeError):
    pass

class InvalidHttpMethodError(ValueError):
    pass

class AuthenticationRequiredError(RuntimeError):
    pass

class KazooApiError(RuntimeError):
    pass
