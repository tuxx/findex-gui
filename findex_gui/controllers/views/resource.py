from bottle import jinja2_template


from findex_gui.controllers.findex.findex import Findex
from findex_gui.controllers.helpers import data_strap


class Resource():
    def __init__(self, db):
        self.db = db
        self.findex = Findex(db=self.db)

    @data_strap
    def overview(self, env):
        data = {
            "resources": self.findex.get_resources()
        }

        return jinja2_template('main/resources_overview', env=env, data=data)