# -*- coding: utf-8 -*-
from datetime import datetime
from bottle import jinja2_template, HTTPResponse

from findex_gui.db.orm import Resources
from findex_gui.controllers.views.browserequest import BrowseRequest
from findex_gui.controllers.findex.findex import Findex
from findex_gui.controllers.helpers import data_strap


class Browse():
    def __init__(self, cfg, db):
        self.cfg = cfg
        self.db = db
        self.findex = Findex(db=self.db)

    @data_strap
    def hosts(self, env):
        data = {'hosts': self.db.query(Resources).all()}

        return jinja2_template('main/browse_hosts', env=env, data=data)

    @data_strap
    def browse(self, path, env):
        try:
            browser = BrowseRequest(db=self.db, findex=self.findex)
            browser.parse(path)

            if not browser.data['isdir']:
                files = browser.fetch_files(file_name=browser.data['file_name'])
                files = browser.prepare_files(files=files, env=env)

                data = {
                    'file': files[0],
                    'breadcrumbs': browser.breadcrumbs(),
                    'data': browser.data
                }

                return jinja2_template('main/browse_file', env=env, data=data)
            else:
                env['time_pageload'] = datetime.now()

                files = browser.fetch_files()
                files = browser.prepare_files(files=files, env=env)

                data = {
                    'files': files,
                    'breadcrumbs': browser.breadcrumbs(),
                    'action_fetches': browser.action_fetches(),
                    'env': browser.data
                }

                env['time_pageload'] = (datetime.now() - env['time_pageload']).total_seconds()

                return jinja2_template('main/browse_dir', env=env, data=data)
        except HTTPResponse as resp:
            return resp
        except Exception as ex:
            print str(ex)
            return jinja2_template('main/error', env=env, data={'error': 'no files were found'})
