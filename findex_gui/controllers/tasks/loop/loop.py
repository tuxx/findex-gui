import settings
import os
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


class TaskLoop:
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
                        last = resource.date_crawl_end
                        if last:
                            if (datetime.now() - last).total_seconds() <= task.options["interval"]:
                                continue

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


