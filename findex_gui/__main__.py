#!/usr/bin/python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from bottle import run, static_file, redirect, response, request, app, route
from bottle import jinja2_template
import bottle, time, os

from findex_common.cfg import Config
from findex_gui.db.orm import Postgres

from findex_gui.controllers.views.home import Home
from findex_gui.controllers.views.browse import Browse
from findex_gui.controllers.views.search import Search

import findex_gui.controllers.findex.themes as themes
from findex_gui.controllers.findex.api import Api

from gevent import monkey
monkey.patch_all()

os.environ['TZ'] = 'Europe/Amsterdam'
time.tzset()

cfg = Config('gui.cfg')
app = app()
database = Postgres(cfg, app)

themes.DATA = themes.Themes(database)

@route('/post', method='POST')
def post(db):
    controller = Api(cfg, db).parse()
    return controller

@route('/')
def root(db):
    controller = Home(cfg, db)
    return controller.root()

@route('/browse')
def browse(db):
    controller = Browse(cfg, db)
    return controller.hosts()

@route('/browse/')
def browse_(db):
    controller = Browse(cfg, db)
    return controller.hosts()

@route('/browse/<path:path>', name='browse')
def browse_dir(path, db):
    if not request.url.endswith('/'):
        redirect('%s/' % request.url)

    controller = Browse(cfg, db)
    return controller.browse(path)

@route('/goto/<path:path>')
def browse_goto(path, db):
    controller = Browse(cfg, db)
    return controller.goto(path)

@route('/search')
def search(db):
    controller = Search(cfg, db)
    return controller.search()

@route('/search/')
def search_(db):
    controller = Search(cfg, db)
    return controller.search()

@route('/static/<filename:path>')
def server_static(filename):
    if filename.endswith(('.py', '.pyc')):
        return
    return static_file(filename, root=os.path.join(os.path.dirname(__file__), 'static'))

@route('/terms')
def terms():
    f = open(os.path.join(os.path.dirname(__file__), 'static', 'terms'))
    response.set_header('content-type', 'text/plain')
    return f.read()

@route('/favicon.ico', method='GET')
def fav():
    return server_static('img/favicon.ico')


@bottle.error(404)
@bottle.error(405)
@bottle.error(500)
@bottle.error(501)
@bottle.error(502)
@bottle.error(503)
@bottle.error(504)
@bottle.error(505)
def error404(error):
    print error
    return jinja2_template('main/error', env={'db_file_count': 0}, data={'error': 'Error - Something happened \:D/'})

@route('/robots.txt')
def beepbeep():
    response.content_type = 'text/plain'
    return "User-agent: *\nDisallow: /browse/\nDisallow: /search\nDisallow: /goto/"


def main():
    run(app=app,
        host=cfg['general']['bind_host'],
        port=cfg['general']['bind_port'],
        quiet=False,
        debug=cfg['general']['debug'],
        reloader=False,
        server='gevent'
    )


if __name__ == "__main__":
    main()
