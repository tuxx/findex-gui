import os
from findex_gui.bin.config import config

from flask import Flask, redirect, url_for
from flask_babel import Babel

from findex_gui.orm.connect import Database

app = None
auth = None
babel = None
locales = None
themes = None

db = Database()
db.connect()

def create_app():
    global app, auth, babel, locales, themes
    app = Flask(import_name=__name__,
                static_folder=None,
                template_folder='themes')

    # setup config
    app.config['SECRET_KEY'] = config("findex:findex:secret_token")
    app.config['dir_base'] = os.path.dirname(os.path.abspath(__file__))
    app.config['dir_root'] = '/'.join(app.config['dir_base'].split('/')[:-1])
    app.config['APPLICATION_ROOT'] = config("findex:findex:application_root")
    app.config['TEMPLATES_AUTO_RELOAD'] = config("findex:findex:debug")
    app.config['PIP_FREEZE'] = []
    SECRET_KEY = config("findex:findex:secret_token")

    # ISO 8601 datetimes
    from findex_gui.bin.utils import ApiJsonEncoder
    app.json_encoder = ApiJsonEncoder

    from findex_gui.bin.utils import dirty_url_for
    dirty_url_for()

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

    # bootstrap db with default values
    db.bootstrap()

    from findex_gui.bin.themes import ThemeController
    themes = ThemeController()

    # init routes
    from findex_gui.controllers.search import routes
    from findex_gui.controllers.browse import routes
    from findex_gui.controllers.relay import routes
    from findex_gui.controllers.user import routes
    from findex_gui.controllers.meta_imdb import routes
    from findex_gui.controllers.news import routes
    from findex_gui.controllers.admin import routes
    from findex_gui.controllers.admin.amqp import routes
    from findex_gui.controllers.admin.server import routes
    from findex_gui.controllers.admin.status import routes
    from findex_gui.controllers.admin.scheduler import routes
    app.add_url_rule('/', endpoint='root', view_func=lambda: redirect(url_for('news_home'), code=302))

    from findex_gui.controllers.search import api
    from findex_gui.controllers.session import api
    from findex_gui.controllers.user import api
    from findex_gui.controllers.browse import api
    from findex_gui.controllers.resources import api
    from findex_gui.controllers.meta_imdb import api
    from findex_gui.controllers.news import api
    from findex_gui.controllers.admin import api
    from findex_gui.controllers.nmap import api
    from findex_gui.controllers.amqp import api
    from findex_gui.controllers.admin.status import api
    from findex_gui.controllers.admin.scheduler import api
    from findex_gui.controllers.admin.logs import api

    return app
