# -*- coding: utf-8 -*-
from bottle import jinja2_template

from findex_gui.db.orm import Resources
from findex_gui.controllers.findex.findex import Findex
from findex_gui.controllers.helpers import data_strap, auth_strap

from findex_gui.controllers.findex.amqp import AmqpController
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

        return jinja2_template('_admin/templates/main/themes_list', env=env, data=data)

    @data_strap
    def bot_list(self, env):
        env['section'] = ['Bots']
        data = {}

        return jinja2_template('_admin/templates/main/bot_list', env=env, data=data)

    @data_strap
    def bot_id(self, bot_id, env):
        data = {}

        crawl = CrawlBots(cfg=self.cfg, db=self.db)
        bot = crawl.get_bot(bot_id)
        if not bot:
            raise Exception("Bot not found")

        data['bot'] = bot
        env['section'] = ['Bots', bot['crawler_name']]

        data['endpoints'] = AmqpController(self.db).all()

        return jinja2_template('_admin/templates/main/bot_id', env=env, data=data)

    @data_strap
    def amqp_list(self, env):
        env['section'] = ['AMQP Endpoints']

        return jinja2_template('_admin/templates/main/amqp_list', env=env)

    @data_strap
    def amqp_add(self, env):
        env['section'] = ['AMQP Endpoints', 'Add']

        return jinja2_template('_admin/templates/main/amqp_add', env=env)

    @data_strap
    def amqp_delete(self, amqp_name, env):
        endpoint = AmqpController(self.db).get(name=amqp_name)
        if not endpoint:
            raise Exception("Endpoint not found")

        env['section'] = ['AMQP Endpoints', 'Delete', amqp_name]
        data = {
            'endpoint': endpoint
        }

        return jinja2_template('_admin/templates/main/amqp_delete', env=env, data=data)

    @data_strap
    def amqp_id(self, amqp_name, env):
        endpoint = AmqpController(self.db).get(name=amqp_name)
        if not endpoint:
            raise Exception('Endpoint not found')

        env['section'] = ['AMQP Endpoints', amqp_name]

        data = {
            'endpoint': dict(endpoint)
        }

        return jinja2_template('_admin/templates/main/amqp_id', env=env, data=data)

    @data_strap
    def task_list(self, env):
        env['section'] = ['Tasks']

        return jinja2_template('_admin/templates/main/task_list', env=env)

    @data_strap
    def task_add(self, env):
        env['section'] = ['Tasks', 'Add']

        return jinja2_template('_admin/templates/main/task_add', env=env)

    @data_strap
    def hostgroup_list(self, env):
        env['section'] = ['Hostgroup', 'List']

        return jinja2_template('_admin/templates/main/hostgroup_list', env=env)