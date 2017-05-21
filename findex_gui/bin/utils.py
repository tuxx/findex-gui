from findex_gui.web import app
import flask

# remove this ~ setup a proper Jinja2 environment
# patch flask.url_for(), prepend APPLICATION_ROOT
# https://github.com/pallets/flask/issues/1714
from flask import url_for as _url_for
from flask import redirect as _redirect
flask.url_for = lambda *args, **kwargs: "%s%s" % (app.config["APPLICATION_ROOT"][:-1],
                                                  _url_for(*args, **kwargs))


def redirect(*args, **kwargs):
    __redirect = _redirect(*args, **kwargs)
    __redirect.autocorrect_location_header = False
    return __redirect
flask.redirect = redirect
