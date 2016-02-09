import requests, json, base64
from datetime import datetime
from requests.auth import HTTPBasicAuth

from findex_gui.db.orm import Crawlers
from findex_gui.bin.time import TimeMagic
from findex_common.exceptions import CrawlBotException
from findex_common.utils import DataObjectManipulation
from findex_gui.controllers.findex.amqp import AmqpController


class CrawlBots():
    def __init__(self, cfg, db):
        self.db = db
        self.cfg = cfg
        self.time = TimeMagic()

        self.webclient_ua = 'Findex GUI'
        self.amqp_consumers = {}

        self.amqp_endpoints = AmqpController(self.db).all()

    def get_bot(self, bot_id):
        bot = self.db.query(Crawlers).filter(Crawlers.id == bot_id).first()
        if bot:
            return self.format(bot)

    def list(self):
        bots = self.db.query(Crawlers).all()
        data = []

        for bot in bots:
            data.append(self.format(bot))

        return data

    def format(self, bot):
        blob = DataObjectManipulation(bot)
        blob = blob.humanize(humandates=True)
        blob = DataObjectManipulation(blob).dictionize()

        blob['last_seen'] = self.time.ago_dt(bot.heartbeat)

        now = datetime.now()
        if (now - bot.heartbeat).total_seconds() > 11:
            blob['status'] = 0  # no need to check other statuses when the heartbeat is too old.
        else:
            blob['status'] = 2

            if bot.jsonrpc:
                check = self._fetch_jsonrpc_status(bot)
                if isinstance(check, CrawlBotException):
                    blob['status'] = 1
                    status = 'ERROR'
                    message = check.message
                else:
                    status = 'OK'
                    message = ''

                blob['status_jsonrpc'] = {
                    'status': status,
                    'message': message
                }
            else:
                blob['status_jsonrpc'] = {
                    'status': 'OFFLINE',
                    'message': ''
                }

            if bot.amqp:
                if bot.amqp_name:
                    check = self._fetch_amqp_status(bot)
                    if isinstance(check, CrawlBotException):
                        blob['status'] = 1
                        status = 'ERROR'
                        message = check.message
                    else:
                        status = 'OK'
                        message = ''

                    blob['status_amqp'] = {
                        'status': status,
                        'message': message
                    }
                else:
                    blob['status_amqp'] = {
                        'status': 'ERROR',
                        'message': 'No AMQP endpoint specified. Click crawlbot details for more information.'
                    }
            else:
                blob['status_amqp'] = {
                    'status': 'OFFLINE',
                    'message': ''
                }

        return blob

    def _fetch_amqp_status(self, bot):
        # ~$ curl -u user:pass "http://<HOST>/api/queues/<VHOST>/<QUEUE>" | python -m json.tool

        endpoint = [z for z in self.amqp_endpoints if z.name == bot.amqp_name]
        if not endpoint:
            bot.amqp_name = ''
            self.db.commit()
            return CrawlBotException('The endpoint to which this bot was assigned to does not exist anymore. Please re-assign an AMQP endpoint.')
        else:
            endpoint = endpoint[0]

        # to-do: support port too, for the web-api
        endpoint_rabbitmq = 'http://%s/api/' % endpoint.host

        ses = requests.session()
        try:
            res = ses.get('%squeues/%s/crawl_queue' % (
                endpoint_rabbitmq,
                endpoint.virtual_host
            ), headers={
                'User-Agent': self.webclient_ua
            }, auth=HTTPBasicAuth(
                endpoint.username,
                endpoint.password)
            , timeout=1)

            if res.status_code == 401:
                raise Exception('RabbitMQ API error. Bad authentication. Please provide AMQP the correct credentials in the administration area.')
            elif res.status_code != 200:
                raise Exception('RabbitMQ API error. HTTP status code was not \'200\' but \'%s\' instead. Failing...' % str(res.status_code))

            content = res.content
            if content == '{"error":"Object Not Found","reason":"\\"Not Found\\"\\n"}':
                return CrawlBotException(message='The RabbitMQ API returned an error. Either the \'vhost\' or \'queue\' settings for AMQP are wrong. Please check if the specified \'vhost\' and/or \'queue\' actually exist within RabbitMQ.')

            blob = json.loads(res.content)

            if not self.amqp_consumers:
                self.amqp_consumers = blob['consumer_details']

            uid = base64.b64encode('%s:%s' % (
                bot.hostname, bot.crawler_name
            ))

            for consumer in self.amqp_consumers:
                if not 'consumer_tag' in consumer:
                    return

                if consumer['consumer_tag'] == uid:
                    return True

            return CrawlBotException(message='Specified AMQP consumer tag not found in RabittMQ queue. Looking for consumer tag: \'%s\'. Does the crawlbot actually have a connection to RabbitMQ and the right queue?' % uid)

        except requests.exceptions.Timeout:
            return CrawlBotException(message='Could not connect to the RabbitMQ API. Is it reachable?<br>Address: %s' % endpoint_rabbitmq)
        except requests.exceptions.ConnectionError:
            return CrawlBotException(message='Could not connect to the RabbitMQ API. Is it reachable?<br>Address: %s' % endpoint_rabbitmq)
        except Exception as ex:
            return CrawlBotException(message=str(ex))

    def _fetch_jsonrpc_status(self, jsonrpc):
        # ~$ curl -X POST http://<HOST> -d '{"params": [], "method": "status"}' | python -m json.tool
        endpoint = 'http://%s:%s' % (
            jsonrpc.jsonrpc_bind_host,
            jsonrpc.jsonrpc_bind_port
        )

        ses = requests.session()
        try:
            res = ses.post(url=endpoint, headers={
                'User-Agent': self.webclient_ua
            }, json={
                'params': [],
                'method': 'status'
            }, timeout=1)

            blob = json.loads(res.content)[0]
            if blob['status'] == '200':
                return 'OK'

            return CrawlBotException(message='Status was NOT OK: \'%s\'' % blob['status'])
        except requests.exceptions.Timeout:
            return CrawlBotException(message='Could not connect to the JSON-RPC API. Is it reachable?<br>Address: %s' % endpoint)
        except requests.exceptions.ConnectionError:
            return CrawlBotException(message="Could not connect to the JSON-RPC API. Is it reachable?<br>Address %s" % endpoint)
        except Exception as ex:
            return CrawlBotException(message=str(ex))