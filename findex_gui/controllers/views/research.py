from bottle import jinja2_template

from findex_gui.controllers.helpers import data_strap


class Research():
    def __init__(self, db):
        self.db = db

    @data_strap
    def research(self, env):
        return jinja2_template('main/research', env=env)

    @data_strap
    def mass_ftp(self, env):
        return jinja2_template('main/research-mass-ftp-crawling', env=env)