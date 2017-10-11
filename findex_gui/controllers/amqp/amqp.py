import json
import string
import random

import pika
from pika import credentials
from findex_common.static_variables import FileProtocols
from findex_gui.controllers.options.options import OptionsController


class AmqpController:
    def __init__(self, username: str, password: str, host: str, vhost: str, queue: str, port: int = 5672):
        self.connection, self.channel = AmqpController.connect(
            username=username,
            password=password,
            host=host,
            vhost=vhost,
            queue=queue,
            port=port
        )

    @staticmethod
    def connect(username: str, password: str, host: str, vhost:str, queue: str, port: int = 5672):
        """
        Connects to an AMQP server
        :return: connection, channel
        """
        creds = credentials.PlainCredentials(username=username, password=password, erase_on_connect=True)
        params = pika.ConnectionParameters(host=host, port=port, virtual_host=vhost, credentials=creds)

        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=queue, durable=True)
        return connection, channel

    def is_connected(self):
        return self._connection is not None and self._channel is not None

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
