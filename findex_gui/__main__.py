#!/usr/bin/python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from bottle import post, get, run, static_file, abort, \
    redirect, response, request, debug, app, route, url, \
    HTTPError, hook, Bottle
from bottle import jinja2_template
import bottle, time
import urllib, os, json, random, jinja2
from datetime import datetime

from findex_common.cfg import Config
from findex_gui.db.orm import Postgres
import findex_gui.bin.utils

from findex_gui.controllers.views.home import Home
from findex_gui.controllers.views.browse import Browse
from findex_gui.controllers.views.documentation import Documentation
from findex_gui.controllers.views.api import Api
from findex_gui.controllers.views.search import Search
from findex_gui.controllers.views.research import Research
from findex_gui.controllers.findex.themes import Themes

from gevent import monkey
monkey.patch_all()

os.environ['TZ'] = 'Europe/Amsterdam'
time.tzset()

cfg = Config()
app = app()
database = Postgres(cfg, app)

themes = Themes(db=database)

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
    return static_file(filename, root=os.path.join(os.path.dirname(__file__), 'static'))

@route('/terms')
def terms():
    f = open('static/terms')
    response.set_header('content-type', 'text/plain')
    return f.read()

@route('/research/')
def research(db):
    controller = Research(db)
    return controller.research()

@route('/research/mass-ftp-crawling/')
def research(db):
    controller = Research(db)
    return controller.mass_ftp()

@route('/documentation/')
def docu(db):
    controllers = Documentation(cfg, db)
    return controllers.docu()


@route('/favicon.ico', method='GET')
def fav():
    return server_static('img/favicon.ico')

@route('/api', method='GET')
def api(db):
    controller = Api(cfg, db)
    return controller.api()


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

if __name__ == "__main__":
    run(app=app,
        host=cfg['general']['bind_host'],
        port=cfg['general']['bind_port'],
        quiet=False,
        debug=cfg['general']['debug'],
        reloader=False,
        server='gevent'
    )