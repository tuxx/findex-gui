import json
import string
import random
from typing import List

import pika
from pika import credentials

from findex_common.static_variables import FileProtocols
from findex_gui.web import db
from findex_gui.bin.utils import log_msg
from findex_gui.controllers.user.roles import role_req
from findex_gui.orm.models import Mq, Resource, NmapRule


class MqConnectionController(object):
    def __init__(self, auth_user: str, auth_pass: str, host: str, vhost: str, queue: str, port: int = 5672):
        self.queue_name = queue
        self.params = pika.ConnectionParameters(
            host=host, port=port, virtual_host=vhost,
            blocked_connection_timeout=2, socket_timeout=2,
            credentials=credentials.PlainCredentials(username=auth_user, password=auth_pass, erase_on_connect=True))
        self.connection = None
        self.channel = None

    def connect(self):
        """Raises an exception on connection errors"""
        pass

    def disconnect(self):
        pass

    def is_connected(self):
        pass

    def send(self, blob: dict):
        pass

    @staticmethod
    def test_amqp(auth_user: str, auth_pass: str, host: str, vhost: str, queue: str, port: int = 5672):
        try:
            amqp = AmqpConnectionController(auth_user, auth_pass, host, vhost, queue, port)
            amqp.connect()
            return True
        except:
            return False

    @staticmethod
    def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
        return "".join(random.choice(chars) for _ in range(size))


class AmqpConnectionController(MqConnectionController):
    def __init__(self, username: str, password: str, host: str, vhost: str, queue: str, port: int = 5672):
        super(AmqpConnectionController, self).__init__(username, password, host, vhost, queue, port)

    def connect(self):
        """Raises an exception on connection errors"""
        # @TODO: implement SSL
        connection = pika.BlockingConnection(self.params)
        channel = connection.channel()
        channel.queue_declare(queue=self.queue_name, durable=True)

        self.connection = connection
        self.channel = channel

    def disconnect(self):
        self.connection.close()

    def is_connected(self):
        return not self.connection.is_closed

    def send_scans(self, scans: List[NmapRule]):
        """
        Sends nmap tasks to available crawlers
        :param scans: nmap rules
        :return:
        """
        tasks = []
        for scan in scans:
            task = {
                "type": "nmap",
                "task": {
                    "rule": scan.rule,
                    "group": scan.group.name
                }
            }
            tasks.append(task)

    def send_resources(self, resources: List[Resource]):
        """
        Sends resource crawl tasks to available crawlers
        :param resources: resources
        :return:
        """
        tasks = []
        for resource in resources:
            task = {
                "type": "crawl",
                "task": {
                    "address": resource.server.address,
                    "method": FileProtocols().name_by_id(resource.protocol),
                    "basepath": resource.basepath,
                    "resource_id": resource.id,
                    "options": {
                        "user-agent": resource.meta.web_user_agent,
                        "recursive_foldersizes": True,
                        "port": resource.port,
                        "auth_user": resource.meta.auth_user,
                        "auth_pass": resource.meta.auth_pass,
                        "depth": resource.meta.depth
                    }
                }
            }
            tasks.append(task)

        for task in tasks:
            self.send(task)

        log_msg("Sent %s tasks to queue %s" % (str(len(tasks)), self.queue_name), category="scheduler")
        self.connection.close()

    def send(self, blob: dict):
        try:
            dumps = json.dumps(blob)
            result = self.channel.basic_publish(
                exchange="",
                routing_key=self.queue_name,
                body=dumps,
                properties=pika.BasicProperties(delivery_mode=2))
            if not result:
                raise Exception(result)

            # debug log here
            return result
        except ValueError:
            return
        except Exception as ex:
            return


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
