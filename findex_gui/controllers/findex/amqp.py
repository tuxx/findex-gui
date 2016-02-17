import pika, sys, json
from pika import exceptions, credentials, spec, BasicProperties

from findex_gui.db.orm import Amqp


class AmqpEndpoint():
    def __init__(self, id, name, username, password, host, port=5672, virtual_host="indexer", queue_name="crawl_queue"):
        self.id = id
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
        for key in ['name', 'username', 'password', 'host', 'port', 'virtual_host', 'queue_name', 'id']:
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
            credentials=creds,
            socket_timeout=2
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


class AmqpController:
    def __init__(self, db):
        self.endpoints = []
        self.db = db

    def get(self, name):
        res = [z for z in self.endpoints if z.name == name]
        if res:
            return res[0]

    def all(self):
        res = self.db.query(Amqp).all()

        data = []
        for amqp_obj in res:
            amqp_endpoint = AmqpEndpoint(
                name=amqp_obj.name,
                username=amqp_obj.username,
                password=amqp_obj.password,
                host=amqp_obj.host,
                port=amqp_obj.port,
                virtual_host=amqp_obj.virtual_host,
                queue_name=amqp_obj.queue_name,
                id=amqp_obj.id
            )

            data.append(amqp_endpoint)

        self.endpoints = data
        return self.endpoints

    def create(self,  **kwargs):
        obj = Amqp(**kwargs)
        self.db.add(obj)
        self.db.commit()

        self.all()
        return True

    def delete(self, name):
        obj = self.db.query(Amqp).filter(Amqp.name == name).first()
        if not obj:
            return False

        self.db.delete(obj)
        self.db.commit()

        # for each bot that was assigned this AMQP endpoint, remove it
        # bots = db.query(Crawlers).filter(Crawlers.amqp_name == args['name']).all()
        # for b in bots:
        #     b.amqp_name = ''
        # db.commit()

        self.all()
        return True

    def loop(self):
        self.all()