from datetime import datetime, date

import flask

from flask import url_for as _url_for, request
from flask import redirect as _redirect
from flask.json import JSONEncoder

from findex_gui.web import app

# dirty flask.url_for() monkey patch.
flask.url_for = lambda *args, **kwargs: "%s%s" % (app.config["APPLICATION_ROOT"][:-1], _url_for(*args, **kwargs))

def redirect(*args, **kwargs):
    __redirect = _redirect(*args, **kwargs)
    __redirect.autocorrect_location_header = False
    return __redirect
flask.redirect = redirect


class ApiJsonEncoder(JSONEncoder):
    '''Custom JSON encoder for flask.jsonify that returns ISO 8601
    strings which can be parsed in javascript with Date.parse()'''
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)
