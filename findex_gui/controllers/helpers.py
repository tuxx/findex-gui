from flask import request, url_for

from findex_gui import app


def redirect_url(default='index'):
    return request.args.get_url('next') or url_for(default) or request.referrer


@app.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response
