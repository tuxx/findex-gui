import settings
from datetime import datetime
import time
import random
import string
import settings
import json
import sys

import pika
from pika import credentials

from findex_common.static_variables import FileProtocols


def console_log(msg):
    print("[%s] %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))


class Db:
    def __init__(self):
        self.db = None

    def connect(self):
        from findex_gui.orm.connect import Postgres
        db = Postgres(app=None, **settings.__dict__)
        db.connect(init=False)
        self.db = db

    def disconnect(self):
        self.db.session.close()
        self.db.engine.dispose()

class Pika:
    def __init__(self):
        self.amqp_queue_name = settings.amqp_queue_name
        self.amqp_username = settings.amqp_username
        self.amqp_password = settings.amqp_password
        self.amqp_host = settings.amqp_host
        self.amqp_vhost = settings.amqp_vhost

        self.channel = None
        self.connection = None

        self.blocking_connect()

    def blocking_connect(self):
        creds = credentials.PlainCredentials(username=self.amqp_username, password=self.amqp_password, erase_on_connect=True)
        params = pika.ConnectionParameters(host=self.amqp_host, port=5672, virtual_host=self.amqp_vhost, credentials=creds)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=self.amqp_queue_name, durable=True)

        self.channel = channel
        self.connection = connection

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
                                       routing_key=self.amqp_queue_name,
                                       body=json.dumps(t),
                                       properties=pika.BasicProperties(
                                           delivery_mode=2
                                       ))

        print(" [x] Sent %s tasks to queue %s" % (str(len(tasks)), self.amqp_queue_name))
        self.connection.close()


class TaskLoop:
    def __init__(self):
        pass

    def blocking_loop(self):
        postgres = Db()
        while True:
            postgres.connect()
            db = postgres.db

            from findex_gui.orm.models import ResourceGroup, Resource, ResourceMeta, ResourceStatus, Task
            resources = []

            for task in db.session.query(Task).all():
                for group in task.groups:
                    for resource in group.parents:
                        # check last crawl time
                        # last = resource.date_crawl_end
                        # if last:
                        #     if (datetime.now() - last).total_seconds() <= task.options["interval"]:
                        #         continue

                        # check busy
                        if resource.meta.status != 0:  # not busy - ResourceStatus().name_by_id
                            continue

                        resources.append(resource)
                        resource.meta.status = 4  # amqp task sent
                        console_log("marked resource %d for crawl")

            if resources:
                db.session.commit()
                db.session.flush()
                p = Pika()
                p.send_tasks(resources)
                console_log("done sending")

            console_log("looped")
            postgres.disconnect()
            sys.exit()
            time.sleep(1)

TaskLoop().blocking_loop()