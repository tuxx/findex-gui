import json
import urllib
from sqlalchemy import and_
from bottle import response

from findex_gui.db.orm import Files, Hosts

from findex_common.utils import ArgValidate
from findex_common.bytes2human import bytes2human


class Api():
    def __init__(self, cfg, db):
        self.cfg = cfg
        self.db = db
        self.arg_validate = ArgValidate()

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
                ).limit(6).all()

                if not results:
                    data[i] = []

                for result in results:
                    host = self.db.query(Hosts).filter_by(id=result.host_id).first()
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