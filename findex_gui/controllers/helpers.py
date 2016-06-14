from flask import request, url_for


def redirect_url(default='index'):
    return request.args.get('next') or url_for(default) or request.referrer
