import os
import settings
import inspect
import flask

from flask import Flask
from flask_restful import Api
from flask_babel import Babel

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

app = Flask(import_name=__name__,
            static_folder=None,
            template_folder='themes')

app.config['SECRET_KEY'] = settings.app_secret
app.config['dir_base'] = os.path.dirname(os.path.abspath(__file__))
app.config['dir_root'] = '/'.join(app.config['dir_base'].split('/')[:-1])
app.config['APPLICATION_ROOT'] = settings.application_root
app.config['TEMPLATES_AUTO_RELOAD'] = settings.app_debug

SECRET_KEY = settings.app_secret


appapi = Api(app)
babel = Babel(app)
#user_timeout
locales = {
    'en': 'English',
    'nl': 'Nederlands'
}

from bin.config import Config
settings = Config()

if not settings.local:
    raise Exception('Local settings (%s/settings.py) not found' % app.config['dir_root'])

import findex_gui.controllers.routes.static
import findex_gui.controllers.routes.errors
import findex_gui.controllers.routes.before_request

from flaskext.auth import Auth
import hashlib
auth = Auth(app)
auth.user_timeout = 604800
auth.hash_algorithm = hashlib.sha256

import orm.connect as db_connect
db_types = {k.lower(): v for k, v in vars(db_connect).items() if inspect.isclass(v) and issubclass(v, db_connect.Orm)}

if not app.config['DB_TYPE'] in db_types:
    raise Exception('Unsupported database type \"%s\". Supported: %s' % (
        app.config['DB_TYPE'],
        ','.join([z.lower() for z in db_types.keys() if not z == 'Orm'])))

db = db_types[app.config['DB_TYPE']](app)
db.connect()

from controllers.themes import ThemeController
themes = ThemeController()

# init routes
import main
from findex_gui.controllers.admin import routes
from findex_gui.controllers.search import routes
from findex_gui.controllers.browse import routes
from findex_gui.controllers.relay import routes
from findex_gui.controllers.user import routes

from findex_gui.controllers.search import api
from findex_gui.controllers.session import api
from findex_gui.controllers.user import api
from findex_gui.controllers.browse import api
from findex_gui.controllers.resources import api
from findex_gui.controllers.tasks import api