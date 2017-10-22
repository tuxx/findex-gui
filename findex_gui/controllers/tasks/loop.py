import json
import subprocess
import os
import logging
import tempfile
from datetime import datetime

import dsnparse
from findex_common.static_variables import FileProtocols
from findex_common.crawl.crawl import CrawlController
from findex_common.nmap import NmapScan

from findex_gui.web import db
from findex_gui.main import python_env
from findex_gui.bin.config import config
from findex_gui.bin.utils import log_msg
from findex_gui.orm.models import NmapRule, ResourceGroup, Resource, ResourceMeta
from findex_gui.controllers.amqp.amqp import AmqpConnectionController
from findex_gui.controllers.resources.resources import ResourceController


class Worker:
    @staticmethod
    def loop():
        tasks = Worker.collect_tasks()
        local_resources = []

        for task in tasks:
            if task.group.mq:
                # fire via AMQP
                if isinstance(task, NmapRule):
                    pass
                elif isinstance(task, Resource):
                    # v = AmqpConnectionController()
                    pass
            else:
                # fire directly, without AMQP
                if isinstance(task, NmapRule):
                    # blocking code
                    nmap = NmapScan(twisted=False)

                    now = datetime.now()
                    scan_results = nmap.scan(task.rule)
                    scan_time = (datetime.now() - now).total_seconds()

                    task.date_scanned = datetime.now()
                    task.output["data"] = {
                        "output": scan_results,
                        "time": scan_time
                    }

                    db.session.commit()
                    db.session.flush()

                    nmap.nmap_to_resource(task, scan_results)
                elif isinstance(task, Resource):
                    local_resources.append(task)

        if local_resources:
            Worker._spawn_crawler(local_resources)

        logging.info("looped")

    @staticmethod
    def collect_tasks(check_resources: bool = True, check_nmap: bool = True):
        tasks = []

        def _skipping(_task, level=1):
            if isinstance(_task, NmapRule):
                log_msg("skipping nmap rule \'%s\': %s" % (_task.name,
                                                           _task.rule), level=level)
            elif isinstance(_task, Resource):
                log_msg("skipping resource \'%s\', protocol: %s" % (_task.server.name,
                                                                    _task.protocol_human), level=level)

        if check_nmap:
            for nmap_rule in db.session.query(NmapRule).filter(NmapRule.status == 0).all():
                if isinstance(nmap_rule.crawl_interval, int) and isinstance(nmap_rule.date_scanned, datetime):
                    # check last scan time
                    if (datetime.now() - nmap_rule.date_scanned).total_seconds() <= nmap_rule.scan_interval:
                        _skipping(nmap_rule, level=0)
                        continue
                elif isinstance(nmap_rule.group.crawl_interval, int) and isinstance(nmap_rule.date_scanned, datetime):
                    if (datetime.now() - nmap_rule.date_scanned).total_seconds() <= nmap_rule.group.crawl_interval:
                        _skipping(nmap_rule, level=0)
                        continue

                tasks.append(nmap_rule)
                nmap_rule.status = 4  # task scheduled
                log_msg("scheduled nmap rule for scanning \'%s\': %s" % (nmap_rule.name, nmap_rule.rule))

            db.session.commit()
            db.session.flush()

        if check_resources:
            for group in db.session.query(ResourceGroup).all():
                crawl_interval = group.crawl_interval

                for resource in group.resources:
                    # # check last crawl time
                    # last = resource.date_crawl_end
                    # if isinstance(last, datetime):
                    #     if (datetime.now() - last).total_seconds() <= crawl_interval:
                    #         continue
                    #
                    # if resource.meta.status != 0:
                    #     continue

                    tasks.append(resource)
                    resource.meta.status = 4  # task scheduled
                    log_msg("scheduled resource \'%s://%s\' (id: %d) for scanning" % (resource.protocol_human,
                                                                                      resource.resource_id, resource.id))
                db.session.commit()
                db.session.flush()
        return tasks

    @staticmethod
    def _spawn_crawler(tasks, queue_size=5):
        """
        Spawns the crawler in 'DIRECT' mode. The suggested way
        is to use AMQP instead.
        :param tasks:
        :param queue_size:
        :return:
        """
        log_msg("Spawning local crawler for %d tasks" % len(tasks))

        # construct tasks json file
        blobs = []
        for t in tasks:
            crawl_message = CrawlController.crawl_message_make(t)
            if not crawl_message:
                continue
            blobs.append(crawl_message)

        try:
            crawl_messages = json.dumps(blobs, indent=4, sort_keys=True)
            crawl_file = tempfile.mkstemp("_fincrawl.json")[1]
        except Exception as ex:
            log_msg(":%s" % (str(ex)), level=3)
            return

        print(crawl_messages)

        # write tmp tasks file for the crawler
        f = open(crawl_file, "w")
        f.write(crawl_messages)
        f.close()

        dsn = dsnparse.parse(config("findex:database:connection"))

        dsn_blob = {
            "user": dsn.username,
            "pass": dsn.password,
            "host": dsn.host,
            "port": 5432 if not isinstance(dsn.port, int) else dsn.port,
            "db": dsn.paths[0]
        }

        # set env variables
        shell_env = os.environ.copy()  # should include the current python virtualenv
        shell_env["FINDEX_CRAWL_MODE"] = "DIRECT"
        shell_env["FINDEX_CRAWL_FILE"] = crawl_file
        shell_env["FINDEX_CRAWL_FILE_CLEANUP"] = ":-D"
        shell_env["FINDEX_CRAWL_LOG_VERBOSITY"] = "20"
        shell_env["FINDEX_CRAWL_QUEUE_SIZE"] = str(queue_size)

        for k, v in dsn_blob.items():
            shell_env["FINDEX_CRAWL_DB_%s" % k.upper()] = str(v)

        for k, v in shell_env.items():
            if k.startswith("FINDEX_CRAWL"):
                print("export %s=\"%s\"" % (k, str(v)))

        # should not block
        command = ["/bin/bash", "-c",
                   "%s/twistd -ony rpc.py &" % os.path.dirname(python_env["interpreter"])]

        print("spawning shell")

        subprocess.Popen(command, cwd="%s/findex-crawl/" % python_env["project_root"],
                         env=shell_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         universal_newlines=True, preexec_fn=os.setpgrp)


worker = Worker()
worker.loop()
