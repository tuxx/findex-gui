import os
from findex_gui.bin.config import config

from flask import Flask
from flask_restful import Api
from flask_babel import Babel


app = Flask(import_name=__name__,
            static_folder=None,
            template_folder='themes')

# setup config
app.config['SECRET_KEY'] = config("findex:findex:secret_token")
app.config['dir_base'] = os.path.dirname(os.path.abspath(__file__))
app.config['dir_root'] = '/'.join(app.config['dir_base'].split('/')[:-1])
app.config['APPLICATION_ROOT'] = config("findex:findex:application_root")
app.config['TEMPLATES_AUTO_RELOAD'] = config("findex:findex:debug")
SECRET_KEY = config("findex:findex:secret_token")

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
from findex_gui.controllers.auth.auth import Auth
import hashlib
auth = Auth(app)
auth.user_timeout = 604800
auth.hash_algorithm = hashlib.sha256

# init database
from findex_gui.orm.connect import Database

db = Database()
db.connect()
db.bootstrap()

from findex_gui.controllers.themes import ThemeController
themes = ThemeController()

# init routes
from findex_gui.controllers.posts.posts import PostController


@app.route("/")
def root():
    posts = PostController.get(limit=5, offset=0)
    return themes.render("main/home", posts=posts)

from findex_gui.controllers.admin import routes
from findex_gui.controllers.search import routes
from findex_gui.controllers.browse import routes
from findex_gui.controllers.relay import routes
from findex_gui.controllers.user import routes
from findex_gui.controllers.meta_imdb import routes

from findex_gui.controllers.search import api
from findex_gui.controllers.session import api
from findex_gui.controllers.user import api
from findex_gui.controllers.browse import api
from findex_gui.controllers.resources import api
from findex_gui.controllers.tasks import api
from findex_gui.controllers.meta_imdb import api
from findex_gui.controllers.posts import api