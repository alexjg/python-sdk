

class InvalidConfigurationError(RuntimeError):
    pass


class InvalidHttpMethodError(ValueError):
    pass


class AuthenticationRequiredError(RuntimeError):
    pass


class KazooApiError(RuntimeError):
    pass


class KazooApiBadDataError(RuntimeError):

    def __init__(self, field_errors):
        super(KazooApiBadDataError, self).__init__("Invalid Data")
        self.field_errors = field_errors

    def __str__(self):
        return "Invalid data, field errors are: {0}".format(self.field_errors)
