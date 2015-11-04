import json
import urllib
from sqlalchemy import and_
from bottle import response, route, HTTPError

from findex_gui.db.orm import Files, Resources
from findex_gui.bin.config import FindexGuiConfig
from findex_gui.controllers.findex.auth import basic_auth
from findex_gui.controllers.findex.crawlers import CrawlBots
import findex_gui.controllers.findex.themes as themes

from findex_common.utils import ArgValidate
from findex_common.bytes2human import bytes2human


cfg = FindexGuiConfig()


@route('/api/crawlbots/list', method='GET')
def crawlbot_list(db):
    auth = basic_auth()
    if isinstance(auth, HTTPError):
        return auth

    crawlbots = CrawlBots(cfg, db)
    data = crawlbots.list()

    return {'crawlbots/list': data}

@route('/api/themes/list', method='GET')
def themes_list(db):
    auth = basic_auth()
    if isinstance(auth, HTTPError):
        return auth

    list = themes.DATA.get_themes()
    active = themes.DATA.get_theme()

    return {
        'themes/list': {
            'list': list,
            'active': active
        }
    }


@route('/api/search/')
def search(db):
    pass


@route('/api/<name>', method='GET')
def recipe_show( name="" ):
    pass


class Api():
    def __init__(self, cfg, db):
        self.cfg = cfg
        self.db = db
        self.arg_validate = ArgValidate()

    def admin_crawlbots_list(self, method='GET'):
        crawls = CrawlBots(self.cfg, self.db)
        data = crawls.list()

        return json.dumps(data)

    def parse(self):
        args = self.arg_validate.verify_args({'cmd': 'string'}, 'POST')
        if isinstance(args, str):
            return json.dumps({'del_task': 'ERR',
                               'msg': 'arg parse error'})

        response.content_type = 'application/json; charset=utf-8'

        if args['cmd'] == 'menu_search_dropdown':
            args = self.arg_validate.verify_args({'val': 'str', 'format': 'int'}, 'POST')
            if isinstance(args, str):
                print ':(1'
                return {'menu_search_dropdown': 'ERR',
                        'msg': args}

            val = args['val'].lower()
            val = val.replace('%', '')

            # length validations
            max_val_length = 22
            min_val_length = 4

            if len(val) >= max_val_length:
                val = val[:max_val_length]
            elif len(val) < min_val_length:
                return {'menu_search_dropdown': 'ERR',
                        'msg': args}

            data = {}
            for i in range(0, 5):
                results = self.db.query(Files).filter(
                    and_(Files.file_isdir == False, Files.searchable.like(val+'%'), Files.file_format == i)
                ).limit(6).list()

                if not results:
                    data[i] = []

                for result in results:
                    host = self.db.query(Resources).filter_by(id=result.resource_id).first()
                    if not host:
                        continue

                    file_name = urllib.unquote_plus(result.file_name)
                    file_path = urllib.unquote_plus(result.file_path)
                    href = '/%s%s' % (host.address, file_path)

                    d = {
                        'file_name': file_name,
                        'file_size': bytes2human(result.file_size),
                        'host': host.address,
                        'path': file_path,
                        'href': href,
                        'format': result.file_format
                    }

                    if not result.file_format in data:
                        data[result.file_format] = [d]
                    else:
                        data[result.file_format].append(d)

            return json.dumps({
                'menu_search_dropdown': 'OK',
                'search_val': val,
                'data': data})