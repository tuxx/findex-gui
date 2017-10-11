import json
import string
import random

import pika
from pika import credentials

from findex_common.static_variables import FileProtocols
from findex_gui.web import db
from findex_gui.controllers.user.roles import role_req
from findex_gui.orm.models import Mq


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

class MqController:
    @staticmethod
    @role_req("ADMIN")
    def add(**kwarg):
        amqp = Mq()
        for k, v in kwarg.items():
            setattr(amqp, k, v)

        try:
            db.session.add(amqp)
            db.session.commit()
            db.session.flush()
        except Exception as ex:
            db.session.rollback()
        return amqp

    @staticmethod
    @role_req("ADMIN")
    def get(uid: int = None, name: str = None, host: str = None, port: int = None,
            limit: int = None, offset: int = None):
        if uid is not None and not isinstance(uid, int):
            raise Exception("uid must be an integer")
        q = db.session.query(Mq)
        if isinstance(uid, int):
            return [q.filter(Mq.id == uid).first()]
        if isinstance(name, str) and name:
            q = q.filter(Mq.name == name)
        if isinstance(host, str) and host:
            q = q.filter(Mq.host == host)
        if isinstance(port, int) and port >= 1:
            q = q.filter(Mq.port == port)

        if isinstance(limit, int):
            q = q.limit(limit)
        if isinstance(offset, int):
            q = q.offset(offset)

        results = q.all()
        return [] if not results else results

    @staticmethod
    @role_req("ADMIN")
    def delete(uid: int):
        if not isinstance(uid, int):
            raise Exception("uid must be an integer")

        try:
            result = db.session.query(Mq).filter(Mq.id == uid).first()
            if not result:
                return True
            result.remove()
            db.session.commit()
            db.session.flush()
            return True
        except:
            db.session.rollback()
            raise
