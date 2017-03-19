# encoding=utf-8
from functools import wraps
from flask import request, Response

from avengersassemble.config import LOGIN_USERNAME, LOGIN_PASSWORD


def _check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == LOGIN_USERNAME and password == LOGIN_PASSWORD


def _authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not _check_auth(auth.username, auth.password):
            return _authenticate()
        return f(*args, **kwargs)

    return decorated
