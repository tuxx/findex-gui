import bottle, os
from bottle import HTTPError, route, app, request, redirect, response, error, jinja2_template, run, static_file
from sqlalchemy.orm import sessionmaker

from findex_common.utils import is_int
from findex_gui.db.orm import Postgres, Options

from findex_gui.controllers.views.home import Home
from findex_gui.controllers.views.browse import Browse
from findex_gui.controllers.views.search import Search
from findex_gui.controllers.views.admin import Admin

import findex_gui.controllers.findex.themes as themes
from findex_gui.controllers.findex.auth import basic_auth
from findex_gui.controllers.findex.api import FindexApi


class FindexApp():
    def __init__(self, cfg):
        self.app = app()
        self.cfg = cfg
        self.db = None
        self.api = None

        setattr(bottle, 'theme', themes.Themes())

        # init default web routes
        self.routes_default()

    def main(self):
        # nuke existing web routes
        self.nuke()

        # install SqlAlchemy bottle.py plugin
        self.hook_db()

        # init API routes
        self.api = FindexApi(self.cfg)

        # init web routes
        @route('/')
        def root(db):
            print self.api
            controller = Home(self.cfg, db)
            return controller.root()

        @route('/browse')
        def browse(db):
            controller = Browse(self.cfg, db)
            return controller.hosts()
        
        @route('/browse/')
        def browse_(db):
            controller = Browse(self.cfg, db)
            return controller.hosts()
        
        @route('/browse/<path:path>', name='browse')
        def browse_dir(path, db):
            if not request.url.endswith('/'):
                redirect('%s/' % request.url)
        
            controller = Browse(self.cfg, db)
            return controller.browse(path)
        
        @route('/goto/<path:path>')
        def browse_goto(path, db):
            controller = Browse(self.cfg, db)
            return controller.goto(path)
        
        @route('/search')
        def search(db):
            controller = Search(self.cfg, db)
            return controller.search()
        
        @route('/search/')
        def search_(db):
            controller = Search(self.cfg, db)
            return controller.search()

        @route('/admin')
        def admin():
            auth = basic_auth()
            if isinstance(auth, HTTPError):
                return auth

            return redirect('/admin/general')

        @route('/admin/')
        def adminx():
            return admin()

        @route('/admin/<name>')
        def admin_dyn(db, name):
            auth = basic_auth()
            if isinstance(auth, HTTPError):
                return auth

            controller = Admin(self.cfg, db)

            try:
                func = getattr(controller, name)
            except:
                return redirect('/admin/general')

            return func()

        @route('/admin/<path:path>')
        def admin_bot(path, db):
            auth = basic_auth()
            if isinstance(auth, HTTPError):
                return auth

            spl = path.split('/')
            controller = Admin(self.cfg, db)

            if not spl[1]:
                redirect('/admin/', 301)

            if spl[0] == 'bot':
                if is_int(spl[1]):
                    return controller.bot_id(spl[1])
                elif spl[1] == 'list':
                    return controller.bot_list()
            elif spl[0] == 'amqp':
                if spl[1] == 'add':
                    return controller.amqp_add()
                elif spl[1] == 'list':
                    return controller.amqp_list()
                elif spl[1] and not len(spl) > 2:
                    return controller.amqp_id(spl[1])
                elif spl[2] == 'delete':
                    return controller.amqp_delete(spl[1])
            elif spl[0] == 'appearance':
                if spl[1] == 'list':
                    return controller.themes()

        @error(404)
        @error(405)
        @error(500)
        @error(501)
        @error(502)
        @error(503)
        @error(504)
        @error(505)
        def error404(error):
            print error
            return jinja2_template('main/error', env={'db_file_count': 0}, data={'error': 'Error - Something happened \:D/'})

    def routes_default(self):
        @route('/static/<filename:path>')
        def server_static(filename):
            if filename.endswith(('.py', '.pyc')):
                return

            return static_file(filename, root=os.path.join(os.path.dirname(__file__), 'static').replace('controllers/findex/', ''))

        @route('/favicon.ico', method='GET')
        def fav():
            return server_static('img/favicon.ico')

        @route('/robots.txt')
        def beepbeep():
            response.content_type = 'text/plain'
            return "User-agent: *\nDisallow: /browse/\nDisallow: /search\nDisallow: /goto/"

        @route('/terms')
        def terms():
            f = open(os.path.join(os.path.dirname(__file__), 'static', 'terms'))
            response.set_header('content-type', 'text/plain')
            return f.read()

        @error(404)
        @error(405)
        @error(500)
        @error(501)
        @error(502)
        @error(503)
        @error(504)
        @error(505)
        def error404(error):
            return str(error)

    def routes_setup(self):
        # remove existing web routes
        self.nuke()

        # init web routes
        @route('/')
        def root():
            return redirect('/install')

        @route('/install')
        def install():
            return jinja2_template('_admin/templates/main/installation')

        @route('/api/findex/writecfg', method='POST')
        def writecfg():
            expected = [
                'database_host',
                'database_port',
                'database_database',
                'database_username',
                'database_password',
                'database_type',
                'database_type',
                'gui_bind_host',
                'gui_bind_port'
            ]

            params = bottle.request.params.dict
            data = {}

            for k, v in params.iteritems():
                if not k in expected:
                    return {
                        'findex/writecfg': {
                            'status': 'FAIL',
                            'message': 'missing %s param' % k
                        }
                    }
                else:
                    if not v[0]:
                        return {
                            'findex/writecfg': {
                                'status': 'FAIL',
                                'message': 'missing value for %s' % k
                            }
                        }

                    spl = k.split('_', 1)
                    section = spl[0]
                    key = spl[1]
                    val = v[0]

                    self.cfg[section][key] = val

            if self.cfg['database']['type'] == 'psql':
                from findex_gui.db.db import Postgres as psql

                connection = psql().test_connection(
                    dbname=self.cfg['database']['database'],
                    user=self.cfg['database']['username'],
                    host=self.cfg['database']['host'],
                    port=self.cfg['database']['port'],
                    password=self.cfg['database']['password']
                )

                if not connection['result']:
                    return {
                        'findex/writecfg': {
                            'status': 'FAIL',
                            'message': connection['message']
                        }
                    }

            # to-do: change these for production
            self.cfg['gui']['debug'] = False
            self.cfg['database']['debug'] = True

            self.cfg.write()

            self.main()

            return {
                'findex/writecfg': {
                    'status': 'OK'
                }
            }

        @route('/api/findex/db_test', method='POST')
        def db_test():
            expected = ['db_host', 'db_port', 'db_name', 'db_user', 'db_password', 'db_type']
            params = bottle.request.params.dict
            data = {}

            for k, v in params.iteritems():
                if not k in expected:
                    return {
                        'findex/db_test': {
                            'status': 'FAIL',
                            'message': 'missing %s param' % k
                        }
                    }
                else:
                    if not v[0]:
                        return {
                            'findex/db_test': {
                                'status': 'FAIL',
                                'message': 'missing value for %s' % k
                            }
                        }

                    data[k] = v[0]

            connection = False

            if data['db_type'] == 'psql':
                from findex_gui.db.db import Postgres as psql

                connection = psql().test_connection(
                    dbname=data['db_name'],
                    user=data['db_user'],
                    host=data['db_host'],
                    port=data['db_port'],
                    password=data['db_password']
                )

            return {
                'findex/db_test': {
                    'status': 'OK' if connection['result'] else 'FAIL',
                    'connection': connection['result'],
                    'message': connection['message']
                }
            }
        
    def nuke(self):
        self.app.routes = []
        self.app.router.static['GET'] = {}
        self.app.dyna_regexes = {}
        self.app.dyna_routes = {}
        self.app.rules = []

        self.api = None

    def populate_db(self):
        ses = sessionmaker(bind=self.db.engine)()

        if not ses.query(Options).filter(Options.key == 'amqp_blob').first():
            ses.add(Options('amqp_blob', '[]'))
        ses.commit()

    def hook_db(self):
        self.db = Postgres(self.cfg, self.app)
        bottle.theme.setup_db(self.db)
        self.populate_db()
        
    def bind(self):
        run(app=self.app,
            host=self.cfg['gui']['bind_host'] if self.cfg.items else '127.0.0.1',
            port=self.cfg['gui']['bind_port'] if self.cfg.items else 2010,
            quiet=False,
            debug=self.cfg['gui']['debug'] if self.cfg.items else True,
            reloader=False,
            server='gevent'
        )
