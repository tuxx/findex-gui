from functools import wraps
from flask import g, request, redirect, url_for


# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if g.user is None:
#             return redirect(url_for('login', next=request.url))
#         return f(*args, **kwargs)
#     return decorated_function


def redirect_url(default='index'):
    return request.args.get('next') or request.referrer or url_for(default)
