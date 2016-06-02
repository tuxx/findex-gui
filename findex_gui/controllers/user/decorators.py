from flask import abort
from functools import wraps

from flask.ext.babel import gettext
from flaskext.auth import get_current_user_data
from flaskext.auth.auth import not_logged_in


def _not_logged_in():
    return abort(401, gettext('Unauthorized'))


def _not_admin():
    return abort(401, gettext('Admin privileges required'))


def admin_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        data = get_current_user_data()

        if data is None:
            return not_logged_in(_not_logged_in, *args, **kwargs)

        elif not data['admin']:
            return not_logged_in(_not_admin, *args, **kwargs)

        return f(*args, **kwargs)
    return decorator