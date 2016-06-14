import os
import settings
import inspect
from flask import Flask
from flask_restful import Api
from flask.ext.babel import Babel

app = Flask(import_name=__name__,
            static_folder=None,
            template_folder='themes')

app.config['SECRET_KEY'] = settings.app_secret
app.config['dir_base'] = os.path.dirname(os.path.abspath(__file__))
app.config['dir_root'] = '/'.join(app.config['dir_base'].split('/')[:-1])
app.config['APPLICATION_ROOT'] = settings.bind_route

SECRET_KEY = open("/dev/random", "rb").read(32)

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

from flaskext.auth import Auth
import hashlib
auth = Auth(app)
auth.user_timeout = 604800
auth.hash_algorithm = hashlib.sha256

# init routes
import main
from findex_gui.controllers.admin import routes
from findex_gui.controllers.search import routes
from findex_gui.controllers.browse import routes
from findex_gui.controllers.user import routes

from findex_gui.controllers.search import api
from findex_gui.controllers.session import api
from findex_gui.controllers.user import api
