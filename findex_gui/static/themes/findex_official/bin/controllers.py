from bottle import jinja2_template
from findex_gui.controllers.helpers import data_strap

from findex_common.utils import ArgValidate


class ThemeControllers():
    def __init__(self, cfg, db):
        self.cfg = cfg
        self.db = db
        self.arg_validate = ArgValidate()

    @data_strap
    def documentation(self, env):
        return jinja2_template('main/documentation', env=env)

    @data_strap
    def api(self, env):
        return jinja2_template('main/api', env=env)

    @data_strap
    def research(self, env):
        return jinja2_template('main/research', env=env)

    @data_strap
    def mass_ftp(self, env):
        return jinja2_template('main/research-mass-ftp-crawling', env=env)