"""Custom exceptions"""
import logging

_log = logging.getLogger(__name__)


class LoggedException(Exception):
    """Exceptions which are being logged"""

    def __init__(self, msg: str = "None", warn: bool = False):
        self.msg = msg
        name = self.__class__.__name__
        if warn:
            _log.warning("%s: %s", name, self.msg)
        else:
            _log.info("%s: %s", name, self.msg)

    def __str__(self):
        return self.msg


class TokenValidationFailed(LoggedException):
    """OAuth token validation fails"""


class Exists(LoggedException):
    """A unique constraint would be violated"""


class NotFound(LoggedException):
    """Result was needed but not found"""
