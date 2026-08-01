"""Module for functions to protect the app from unwanted access."""

#region Imports
from functools import wraps

from expiring_dict import ExpiringDict
from flask import abort, redirect, request, session

from . import const, database
#endregion

#region Global variables 
_failed_logins: ExpiringDict[str, int] = ExpiringDict(const.api.MAX_LOGIN_LOCKOUT_SECONDS)
#endregion

#region Functions
def is_ip_blocked(ip: str) -> bool:
    return ip in _failed_logins and _failed_logins[ip] >= const.api.MAX_LOGIN_ATTEMPTS

def log_failed_login(ip: str):
    _failed_logins[ip] = _failed_logins.get(ip, 0) + 1

def login_user(username: str, password: str) -> bool:
    """Login user with credentials given.
       Returns whether the login was successful."""

    row = database.validateuser(username, password)
    if row:
        session.clear()
        session[const.users.keys.LOGIN_STATUS] = True
        session[const.users.keys.ID] = row[const.users.keys.ID]
        session[const.users.keys.NAME] = row[const.users.keys.NAME]
        for permission in const.users.PERMISSIONS:
            session[permission] = bool(row[permission])
        return True
    else:
        return False
#endregion

#region Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get(const.users.keys.LOGIN_STATUS):
            return redirect(url_for('pages.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get(const.users.PERMISSIONS.ADMIN):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def deletion_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get(const.users.PERMISSIONS.DELETE):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def block_repeated_attempts(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if is_ip_blocked(request.remote_addr):
            abort(429)
        return f(*args, **kwargs)
    return decorated_function
#endregion