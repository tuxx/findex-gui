import jinja2
from bottle import hook, response

@hook('after_request')
def enable_cors():
    response.headers['X-Pirate'] = 'Yarrr'
