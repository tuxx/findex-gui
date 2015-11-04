from bottle import route

from findex_gui.static.themes.findex_official.bin.controllers import ThemeControllers
from findex_gui.bin.config import FindexGuiConfig

cfg = FindexGuiConfig()


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