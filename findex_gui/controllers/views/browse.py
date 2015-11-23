# -*- coding: utf-8 -*-
from datetime import datetime
from bottle import jinja2_template

from findex_gui.db.orm import Resources
from findex_gui.controllers.views.browser import Browser
from findex_gui.controllers.findex.findex import Findex
from findex_gui.controllers.helpers import data_strap


class Browse():
    def __init__(self, cfg, db):
        self.cfg = cfg
        self.db = db
        self.findex = Findex(db=self.db)

    @data_strap
    def hosts(self, env):
        data = {'hosts': self.db.query(Resources).list()}

        return jinja2_template('main/browse_hosts', env=env, data=data)

    @data_strap
    def browse(self, path, env):
        env['time_pageload'] = datetime.now()

        try:
            browser = Browser(db=self.db, findex=self.findex, path=path)
            browser.fetch_files()
            browser.prepare_files(env=env)

            data = {
                'files': browser.files,
                'breadcrumbs': browser.breadcrumbs(),
                'action_fetches': browser.generate_action_fetches(),
                'env': browser.data
            }

            env['time_pageload'] = (datetime.now() - env['time_pageload']).total_seconds()

            return jinja2_template('main/browse_dir', env=env, data=data)
        except Exception as ex:
            print str(ex)
            return jinja2_template('main/error', env=env, data={'error': 'no files were found'})

    @data_strap
    def goto(self, path, env):
        try:
            uid = int(path)

            f = self.findex.get_files_objects(id=uid)

            if not f:
                raise Exception()

            f = f[0]

            h = self.db.query(Resources).filter_by(
                id=f.resource_id
            ).first()

            if f and h:
                data = {
                    'file': f,
                    'host': h
                }
            else:
                raise Exception()

            return jinja2_template('main/browse_goto', env=env, data=data)
        except Exception as ex:
            return 'error :( we could always stay here'
