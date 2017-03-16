from flask import abort, request
from functools import wraps

from flask_babel import gettext
from flaskext.auth import get_current_user_data
from flaskext.auth.auth import not_logged_in

from findex_gui.controllers.user.user import UserController


def _not_logged_in():
    return abort(401, gettext('Unauthorized'))


def _not_admin():
    return abort(401, gettext('Admin privileges required'))


def admin_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not UserController.is_admin():
            return not_logged_in(_not_admin, *args, **kwargs)

        return f(*args, **kwargs)
    return decorator


def login_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        data = get_current_user_data()

        if data is None:
            if request.authorization:
                if UserController.authenticate_basic(inject=True):
                    return f(*args, **kwargs)

            return not_logged_in(_not_logged_in, *args, **kwargs)

        return f(*args, **kwargs)
    return decorator