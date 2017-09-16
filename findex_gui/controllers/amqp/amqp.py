import json
import string
import random

import pika
from pika import credentials
from findex_common.static_variables import FileProtocols
from findex_gui.bin.config import config
from findex_gui.controllers.options.options import OptionsController


class AmqpController:
    def __init__(self, amqp_name):
        self.amqp_name = amqp_name

        self.connected = False
        self._connection = None
        self._channel = None

    def connect_via_name(self, amqp_name):
        from findex_gui.controllers.options.options import OptionsController

        OptionsController.get('amqp')

    def connect(self):
        creds = credentials.PlainCredentials(username=self.username, password=self.password, erase_on_connect=True)
        params = pika.ConnectionParameters(host=self.host, port=5672, virtual_host=self.vhost, credentials=creds)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=self.queue_name, durable=True)

    def

    def is_connected(self):
        return self.connection is not None and self.channel is not None

    @staticmethod
    def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def send_tasks(self, resources):
        """
        converts resource objects to crawl requests
        :param resources: a list of resources
        :return:
        """
        tasks = []

        for resource in resources:
            t = {
                "address": resource.server.address,
                "method": FileProtocols().name_by_id(resource.protocol),
                "basepath": resource.basepath,
                "resource_id": resource.id,
                "options": {
                    "user-agent": resource.meta.web_user_agent,
                    "recursive_foldersizes": True,
                    "port": resource.port,
                    "auth_user": resource.meta.auth_user,
                    "auth_pass": resource.meta.auth_pass
                }
            }
            tasks.append(t)

        for t in tasks:
            self.channel.basic_publish(exchange='',
                                       routing_key=self.queue_name,
                                       body=json.dumps(t),
                                       properties=pika.BasicProperties(
                                           delivery_mode=2
                                       ))

        print(" [x] Sent %s tasks to queue %s" % (str(len(tasks)), self.queue_name))
        self.connection.close()

    @staticmethod
    def get_credentials():
        options_key = "amqp_credentials"
        settings = OptionsController.get(options_key)
        return settings