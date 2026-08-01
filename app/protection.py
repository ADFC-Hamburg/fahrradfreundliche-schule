"""Module for functions to protect the app from unwanted access."""

#region Imports
from functools import wraps

from expiring_dict import ExpiringDict
from flask import abort, request

from . import const
#endregion

#region Global variables 
_failed_logins: ExpiringDict[str, int] = ExpiringDict(const.api.MAX_LOGIN_LOCKOUT_SECONDS)
#endregion

#region Functions
def is_ip_blocked(ip: str) -> bool:
    return ip in _failed_logins and _failed_logins[ip] >= const.api.MAX_LOGIN_ATTEMPTS

def log_failed_login(ip: str):
    _failed_logins[ip] = _failed_logins.get(ip, 0) + 1
#endregion

#region Decorators
def block_repeated_attempts(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if is_ip_blocked(request.remote_addr):
            abort(429)
        return f(*args, **kwargs)
    return decorated_function
#endregion