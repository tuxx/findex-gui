import bottle
from bottle import response, route, HTTPError

from findex_gui.bin.config import FindexGuiConfig
from findex_gui.controllers.findex.crawlers import CrawlBots
from findex_gui.controllers.helpers import auth_strap, data_strap
from findex_gui.controllers.views.searcher import Searcher

from findex_common.utils import ArgValidate


class FindexApi():
    def __init__(self, cfg):
        self.cfg = cfg
        self.arg_validate = ArgValidate()

        self.routes()

    def routes(self):
        global route

        @route('/api/<path:path>', method=['GET', 'POST'])
        def dyn(path, db):
            path = path.replace('/', '_')

            try:
                func = getattr(self, path)
            except:
                return {
                    'nope': 'nope'
                }

            return func(db)

    @auth_strap
    def bots_list(self, db, env):
        bot_list = CrawlBots(self.cfg, db)
        data = bot_list.list()

        return {'bots/list': data}

    @auth_strap
    def themes_list(self, db, env):
        list = bottle.theme.get_themes()
        active = bottle.theme.active_theme['name']

        return {
            'themes/list': {
                'list': list,
                'active': active
            }
        }

    def search(self, db):
        params = bottle.request.params.dict

        #data = Searcher(cfg=self.cfg, db=db, env={}).search(params)