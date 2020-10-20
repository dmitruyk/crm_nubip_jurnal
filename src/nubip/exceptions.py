
class BaseEx(Exception):
    CODE = 500
    MESSAGE = 'server_error'

    def __init__(self, errors=None):
        if isinstance(errors, (str, int)):
            self.errors = [errors]
        elif errors is None:
            self.errors = [self.MESSAGE]
        elif isinstance(errors, (list, tuple)):
            self.errors = errors
        else:
            raise TypeError('Unknown type')


class BadRequestException(BaseEx):
    CODE = 400
    MESSAGE = 'bad_request'


class UnauthorizedException(BaseEx):
    CODE = 401
    MESSAGE = 'request__unauthorized'


class ForbiddenException(BaseEx):
    CODE = 403
    MESSAGE = 'request__forbidden'


class NotFoundException(BaseEx):
    CODE = 404
    MESSAGE = 'not_found'


class ServerUnavailableException(BaseEx):
    CODE = 503
    MESSAGE = 'service__unavailable'


class ServerInternalErrorException(BaseEx):
    CODE = 500
    MESSAGE = 'service__internal_error'


iterable = [
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ServerUnavailableException
]
