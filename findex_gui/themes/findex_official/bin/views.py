from bottle import route

from findex_gui.themes.findex_official.bin.controllers import ThemeControllers
from findex_gui.bin.config import FindexGuiConfig

from findex_gui.controllers.views.home import Home
from findex_gui.controllers.views.browse import Browse
from findex_gui.controllers.views.search import Search

cfg = FindexGuiConfig()


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


@route('/search')
def search(db):
    controller = Search(cfg, db)
    return controller.search()


@route('/browse/<path:path>', name='browse')
def browse_dir(path, db):
    controller = Browse(cfg, db)
    return controller.browse(path)


@route('/api', method='GET')
def api(db):
    controller = ThemeControllers(cfg, db)
    return controller.api()


@route('/research/')
def research(db):
    controller = ThemeControllers(cfg, db)
    return controller.research()


@route('/research/mass-ftp-crawling/')
def research(db):
    controller = ThemeControllers(cfg, db)
    return controller.mass_ftp()


@route('/documentation/')
def docu(db):
    controller = ThemeControllers(cfg, db)
    return controller.documentation()