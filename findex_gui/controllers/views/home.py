from bottle import jinja2_template

from findex_gui.controllers.findex.findex import Findex
from findex_gui.controllers.helpers import data_strap


class Home():
    def __init__(self, cfg, db):
        self.cfg = cfg
        self.db = db
        self.findex = Findex(db=self.db)

    @data_strap
    def root(self, env):
        return jinja2_template('main/home', env=env)
