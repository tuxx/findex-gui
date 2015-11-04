# -*- coding: utf-8 -*-
from bottle import jinja2_template

from findex_gui.db.orm import Resources
from findex_gui.controllers.findex.findex import Findex
from findex_gui.controllers.helpers import data_strap


from findex_gui.controllers.findex.crawlers import CrawlBots


class Admin():
    def __init__(self, cfg, db):
        self.cfg = cfg
        self.db = db
        self.findex = Findex(db=self.db)

    @data_strap
    def admin(self, env):
        data = {}

        crawls = CrawlBots(cfg=self.cfg, db=self.db)
        data['bots'] = crawls.list()

        return jinja2_template('admin', env=env, data=data)