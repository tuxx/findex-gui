from functools import wraps
from datetime import datetime

from flask import request, url_for, jsonify

from findex_gui.bin.config import config
from findex_gui.web import app


def redirect_url(default='index'):
    return request.args.get_url('next') or url_for(default) or request.referrer


@app.after_request
def after_request(r):
    r.headers.add('Accept-Ranges', 'bytes')

    if config("findex:findex:debug"):
        r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        r.headers["Pragma"] = "no-cache"
        r.headers["Expires"] = "0"
        r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.errorhandler(404)
def error(e):
    from findex_gui.web import themes
    return themes.render("main/error", msg=str(e))
