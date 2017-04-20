import os
import settings

from flask import Flask
from flask_restful import Api
from flask_babel import Babel


app = Flask(import_name=__name__,
            static_folder=None,
            template_folder='themes')

# setup config
app.config['SECRET_KEY'] = settings.app_secret
app.config['dir_base'] = os.path.dirname(os.path.abspath(__file__))
app.config['dir_root'] = '/'.join(app.config['dir_base'].split('/')[:-1])
app.config['APPLICATION_ROOT'] = settings.application_root
app.config['TEMPLATES_AUTO_RELOAD'] = settings.app_debug
SECRET_KEY = settings.app_secret

# setup api
appapi = Api(app)

# setup translations
babel = Babel(app)
locales = {
    'en': 'English',
    'nl': 'Nederlands'
}

# init some flask stuff
import findex_gui.bin.utils
import findex_gui.controllers.routes.static
import findex_gui.controllers.routes.errors
import findex_gui.controllers.routes.before_request

# init user authentication
from flaskext.auth import Auth
import hashlib
auth = Auth(app)
auth.user_timeout = 604800
auth.hash_algorithm = hashlib.sha256

# init database
from findex_gui.orm.connect import Database

db = Database(hosts=settings.db_hosts,
              user=settings.db_user,
              passwd=settings.db_pass,
              port=settings.db_port,
              name=settings.db_name)
db.connect()
db.bootstrap()

from findex_gui.controllers.themes import ThemeController
themes = ThemeController()

# init routes
from findex_gui import main
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