import bottle, json
from bottle import response, route, HTTPError

from findex_gui.controllers.findex.amqp import AmqpEndpoint
from findex_gui.bin.config import FindexGuiConfig
from findex_gui.controllers.findex.crawlers import CrawlBots
from findex_gui.controllers.findex.amqp import AmqpController
from findex_gui.controllers.helpers import auth_strap, data_strap
from findex_gui.controllers.views.searcher import Searcher
from findex_common.resourcetypes import get_protocol_from_int, get_protocol_id_from_name
from findex_gui.db.orm import Crawlers

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
                if path.startswith('_'):
                    raise Exception()

                func = getattr(self, path)
            except Exception as ex:
                return {
                    'nope': 'nope'
                }

            return func(db)

    @auth_strap
    def bot_list(self, db, env):
        controller = CrawlBots(self.cfg, db)
        data = controller.list()

        return {'bot/list': data}

    @auth_strap
    def bot_assign_amqp_endpoint(self, db, env):
        args = ArgValidate().verify_args({
            'bot_id': int,
            'amqp_endpoint_name': str
        }, 'POST')
        if not isinstance(args, dict):
            return {
                'bot/assign_amqp_endpoint': {
                    'status': 'FAIL',
                    'message': str(args)
                }
            }

        bot = db.query(Crawlers).filter(Crawlers.id == args['bot_id']).first()

        if not bot:
            return {
                'bot/assign_amqp_endpoint': {
                    'status': 'FAIL',
                    'message': 'no bot by that id'
                }
            }

        endpoint = AmqpController(db).get(args['amqp_endpoint_name'])
        if not endpoint:
            return {
                'bot/assign_amqp_endpoint': {
                    'status': 'FAIL',
                    'message': 'no amqp endpoint by that id'
                }
            }

        bot.amqp_name = endpoint.name
        db.commit()

        return {
            'bot/assign_amqp_endpoint': {
                'status': 'OK'
            }
        }

    @auth_strap
    def themes_list(self, db, env):
        active = bottle.loops['themes'].active
        data = [v for k,v in bottle.loops['themes'].data.iteritems() if not v['theme_name'] == active]
        active = bottle.loops['themes'].data[active]
        data.insert(0, active)

        return {
            'themes/list': {
                'list': data,
                'active': active
            }
        }

    @auth_strap
    def themes_switch(self, db, env):
        args = ArgValidate().verify_args({
            'name': str
        }, 'POST')
        if not isinstance(args, dict):
            return {
                'themes/switch': {
                    'status': 'FAIL',
                    'message': str(args)
                }
            }

        res = bottle.loops['themes'].set(args['name'])
        if not res:
            return {
                'themes/switch': {
                    'status': 'FAIL',
                    'message': 'no such theme %s or theme already active' % args['name']
                }
            }

        return {
            'themes/switch': {
                'status': 'OK'
            }
        }

    @auth_strap
    def amqp_list(self, db, env):
        endpoints = bottle.loops['amqp'].endpoints
        data = []

        for endpoint in endpoints:
            blob = dict(endpoint)
            blob['password'] = '****'
            data.append(blob)

        return {
            'amqp/list': data
        }

    def _amqp_test(self, db):
        args = ArgValidate().verify_args({
            'host': str,
            'port': int,
            'username': str,
            'password': str,
            'type': str,
            'name': str,
            'vhost': str
        }, 'POST')

        if not isinstance(args, dict):
            return Exception(args)

        # check for duplicates based on endpoint name
        endpoint = AmqpController(db).get(args['name'])
        if endpoint:
            return Exception('Duplicate AMQP endpoint name')

        endpoint = AmqpEndpoint(
            name=args['name'],
            username=args['username'],
            password=args['password'],
            host=args['host'],
            port=args['port'],
            virtual_host=args['vhost'],
            id=-1
        )

        try_connect = endpoint.connect()
        if isinstance(try_connect, Exception):
            return Exception(try_connect)

        endpoint.close()
        return endpoint

    @auth_strap
    def amqp_test(self, db, env):
        endpoint = self._amqp_test(db)
        if isinstance(endpoint, Exception):
            return {
                'amqp/test': {
                    'status': 'FAIL',
                    'message': str(endpoint)
                }
            }

        return {
            'amqp/test': {
                'status': 'OK'
            }
        }

    @auth_strap
    def amqp_add(self, db, env):
        endpoint = self._amqp_test(db)
        if isinstance(endpoint, Exception):
            return {
                'amqp/add': {
                    'status': 'FAIL',
                    'message': str(endpoint)
                }
            }

        bottle.loops['amqp'].create(**dict(endpoint))

        return {
            'amqp/add': {
                'status': 'OK'
            }
        }

    @auth_strap
    def amqp_delete(self, db, env):
        args = ArgValidate().verify_args({
            'name': str
        }, 'POST')
        if not isinstance(args, dict):
            return {
                'amqp/delete': {
                    'status': 'FAIL',
                    'message': str(args)
                }
            }

        bottle.loops['amqp'].delete(args['name'])

        return {
            'amqp/delete': {
                'status': 'OK'
            }
        }

    @auth_strap
    def targets_add(self, db, env):
        args = ArgValidate().verify_args({
            'type': str
        }, 'POST')

        if not isinstance(args, dict):
            return {
                'targets/add': {
                    'status': 'FAIL',
                    'message': str(args)
                }
            }

        if args['type'] == 'single':
            self._targets_add_single(db, args)

    def _targets_add_single(self, db, args):
        # to-do: rewrite/modify argvalidate, init twice is ugly
        args = ArgValidate().verify_args({
            'inputSingleMethod': str,
            'inputSingleName': str,
            'inputSingleHost': str,
            'inputSingleAMQP': int
        }, 'POST')

        if not isinstance(args, dict):
            return {
                'targets/add': {
                    'status': 'FAIL',
                    'message': str(args)
                }
            }

        amqp = [z for z in bottle.loops['amqp'].endpoints if z.id == args['inputSingleAMQP']]
        if not amqp:
            return {
                'targets/add': {
                    'status': 'FAIL',
                    'message': str(args)
                }
            }
        amqp = amqp[0]

        name = args['inputSingleName']
        protocol = get_protocol_id_from_name(args['inputSingleMethod'])
        address = args['inputSingleHost']

        # to-do: nope
        port = 0
        try:
            port = int(args['inputSinglePort'])
        except:
            pass

        from findex_gui.db.orm import Targets

        basepath = args['inputSingleBasepath']
        auth_username = args['inputSingleOptUsername']
        auth_password = args['inputSingleOptPassword']
        display_url = args['inputSingleOptDisplayUrl']
        user_agent = args['inputSingleOptUserAgent']
        recursive_sizes = args['inputSingleRecursiveDirSizes']

        if recursive_sizes:
            recursive_sizes = True if recursive_sizes == 'on' else False

        # to-do: replace by TargetController.add()
        from findex_gui.db.orm import Targets
        t = Targets(
            name=name,
            address=address,
            protocol=protocol,
            basepath=basepath,
            port=port,
            auth_username=auth_username,
            auth_password=auth_password,
            display_url=display_url,
            user_agent=user_agent,
            recursive_sizes=recursive_sizes,
            amqp_id=amqp.id
        )
        e = ''

    def search(self, db):
        params = bottle.request.params.dict

        #data = Searcher(cfg=self.cfg, db=db, env={}).search(params)