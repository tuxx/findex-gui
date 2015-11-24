import pika, sys, json
from pika import exceptions, credentials, spec, BasicProperties

from findex_gui.db.orm import Options


class AmqpEndpoint():
    def __init__(self, name, username, password, host, port=5672, virtual_host="indexer", queue_name="crawl_queue"):
        self.name = name
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.virtual_host = virtual_host
        self.queue_name = queue_name

        self.connection = None
        self.channel = None

    def __iter__(self):
        for key in ['name', 'username', 'password', 'host', 'port', 'virtual_host', 'queue_name']:
            yield (key, getattr(self, key))

    def connect(self):
        creds = credentials.PlainCredentials(
            username=self.username,
            password=self.password,
            erase_on_connect=True
        )

        params = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            virtual_host=self.virtual_host,
            credentials=creds
        )

        try:
            connection = pika.BlockingConnection(params)
            self.channel = connection.channel()
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=True
            )

        except pika.exceptions.ConnectionClosed as ex:
            return Exception("Connection Error")
        except pika.exceptions.ProbableAuthenticationError:
            return Exception("Authentication error")
        except pika.exceptions.ProbableAccessDeniedError:
            return Exception("Authentication error - login was successful but could not access vhost")
        except Exception as ex:
            return Exception("Error: %s" % str(type(ex)))

    def close(self):
        if self.connection:
            self.connection.close()

    def publish_message(self, body):
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2
            )
        )


class Amqp():
    def __init__(self, db):
        self.db = db

    def _get_endpoints(self):
        res = self.db.query(Options).filter(Options.key == 'amqp_blob').first()
        if not res:
            self.db.add(Options('amqp_blob', '[]'))
            self.db.commit()
            return self.db.query(Options).filter(Options.key == 'amqp_blob').first()
        return res

    def _set_endpoint(self, val):
        res = self.db.query(Options).filter(Options.key == 'amqp_blob').first()
        res.val = val
        self.db.commit()

    def get_endpoint(self, name):
        endpoints = self.get_endpoints()

        for endpoint in endpoints:
            if endpoint.name == name:
                return endpoint

    def get_endpoints(self):
        res = self._get_endpoints()

        if not res.val:
            return []

        try:
            blob = json.loads(res.val)
            data = []

            for endpoint in blob:
                amqp_endpoint = AmqpEndpoint(
                    name=endpoint['name'],
                    username=endpoint['username'],
                    password=endpoint['password'],
                    host=endpoint['host'],
                    port=endpoint['port'],
                    virtual_host=endpoint['virtual_host'],
                    queue_name=endpoint['queue_name']
                )

                data.append(amqp_endpoint)

            return data
        except:
            res.val = '[]'
            self.db.commit()

        return []

    def set_endpoint(self, **kwargs):
        if not 'endpoint' in kwargs:
            endpoint = AmqpEndpoint(
                name=kwargs['name'],
                username=kwargs['username'],
                password=kwargs['password'],
                host=kwargs['host'],
                port=kwargs['port'],
                virtual_host=kwargs['vhost']
            )
        else:
            endpoint = kwargs['endpoint']

        # validation
        try_connect = endpoint.connect()
        if isinstance(try_connect, Exception):
            return try_connect

        # clear connection
        endpoint.close()

        data = dict(endpoint)
        endpoints = self.get_endpoints()
        endpoints_json = []

        for endpoint in endpoints:
            if data['name'] == endpoint.name:
                return Exception("Duplicate endpoint name error")

            endpoints_json.append(dict(endpoint))

        endpoints_json.append(data)
        blob = json.dumps(endpoints_json)

        self._set_endpoint(blob)

    def del_endpoint(self, name):
        endpoints = self.get_endpoints()

        data = []

        for d in endpoints:
            if not d.name == name:
                data.append(dict(d))

        blob = json.dumps(data)
        self._set_endpoint(blob)