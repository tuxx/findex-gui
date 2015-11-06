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
    def general(self, env):
        env['section'] = ['General']
        data = {}

        return jinja2_template('_admin/templates/main/general', env=env, data=data)

    @data_strap
    def themes(self, env):
        env['section'] = ['Themes']
        data = {}

        return jinja2_template('_admin/templates/main/themes', env=env, data=data)

    @data_strap
    def bots(self, env):
        env['section'] = ['Bots']
        data = {}

        return jinja2_template('_admin/templates/main/bots', env=env, data=data)

    @data_strap
    def bot(self, bot_id, env):
        data = {}

        crawl = CrawlBots(cfg=self.cfg, db=self.db)
        bot = crawl.get_bot(bot_id)

        data['bot'] = bot
        env['section'] = ['Bots', bot['crawler_name']]

        return jinja2_template('_admin/templates/main/bot', env=env, data=data)