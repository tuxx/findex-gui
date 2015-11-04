import bottle, os
from bottle import HTTPError, route, app, request, redirect, response, error, jinja2_template, run, static_file

from findex_gui.db.orm import Postgres

from findex_gui.controllers.views.home import Home
from findex_gui.controllers.views.browse import Browse
from findex_gui.controllers.views.search import Search
from findex_gui.controllers.views.admin import Admin

import findex_gui.controllers.findex.themes as themes
from findex_gui.controllers.findex.auth import basic_auth
from findex_gui.controllers.findex.api import Api


class FindexApp():
    def __init__(self, cfg):
        self.app = app()
        self.cfg = cfg
        self.db = None

        setattr(bottle, 'theme', themes.Themes())
        
        self.routes_default()

    def routes_main(self):
        self.routes_nuke()

        self.hook_db()

        @route('/admin')
        def admin(db):
            auth = basic_auth()
            if isinstance(auth, HTTPError):
                return auth

            controller = Admin(self.cfg, db)
            return controller.admin()

        @route('/post', method='POST')
        def post(db):
            controller = Api(self.cfg, db).parse()
            return controller
        
        @route('/')
        def root(db):
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
            print error
            return jinja2_template('main/error', env={'db_file_count': 0}, data={'error': 'Error - Something happened \:D/'})

    def routes_default(self):
        @route('/static/<filename:path>')
        def server_static(filename):
            if filename.endswith(('.py', '.pyc')):
                return
            return static_file(filename, root=os.path.join(os.path.dirname(__file__), 'static'))

        @route('/favicon.ico', method='GET')
        def fav():
            return server_static('img/favicon.ico')

        @route('/robots.txt')
        def beepbeep():
            response.content_type = 'text/plain'
            return "User-agent: *\nDisallow: /browse/\nDisallow: /search\nDisallow: /goto/"

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
        self.routes_nuke()

        @route('/')
        def root():
            return redirect('/install')

        @route('/install')
        def install():
            return jinja2_template('installation')

        @route('/api/findex/writecfg', method='POST')
        def writecfg():
            expected = ['db_host', 'db_port', 'db_name', 'db_user', 'db_password', 'db_type', 'gui_host', 'gui_port']
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

                    data[k] = v[0]

            if data['db_type'] == 'psql':
                from findex_gui.db.db import Postgres as psql

                connection = psql().test_connection(
                    dbname=data['db_name'],
                    user=data['db_user'],
                    host=data['db_host'],
                    port=data['db_port'],
                    password=data['db_password']
                )

                if not connection['result']:
                    return {
                        'findex/writecfg': {
                            'status': 'FAIL',
                            'message': connection['message']
                        }
                    }

            self.cfg.db_host = data['db_host']
            self.cfg.db_port = data['db_port']
            self.cfg.db_user = data['db_user']
            self.cfg.db_password = data['db_password']
            self.cfg.db_name = data['db_name']
            self.cfg.db_type = data['db_type']

            self.cfg.gui_host = data['gui_host']
            self.cfg.gui_port = data['gui_port']
            self.cfg.write()

            self.cfg.load()

            self.routes_main()

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
        
    def routes_nuke(self):
        self.app.routes = []
        self.app.router.static['GET'] = {}
        self.app.dyna_regexes = {}
        self.app.dyna_routes = {}
        self.app.rules = []

    def hook_db(self):
        self.db = Postgres(self.cfg, self.app)
        bottle.theme.setup_db(self.db)
        
    def bind(self):
        run(app=self.app,
            host=self.cfg['gui']['bind_host'] if self.cfg.items else '127.0.0.1',
            port=self.cfg['gui']['bind_port'] if self.cfg.items else 2010,
            quiet=False,
            debug=self.cfg['gui']['debug'] if self.cfg.items else True,
            reloader=False,
            server='gevent'
        )
