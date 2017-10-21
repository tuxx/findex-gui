from datetime import datetime
import logging
import random

from findex_gui.web import db
from findex_gui.bin.utils import log_msg
from findex_gui.orm.models import NmapRule, Logging, ResourceGroup
from findex_gui.controllers.amqp.amqp import AmqpConnectionController
from findex_gui.controllers.resources.resources import ResourceController
from findex_common.static_variables import FileProtocols
from findex_common.nmap import NmapScan


class Worker:
    @staticmethod
    def _spawn_crawler(tasks_resources, tasks_nmap, queue_size=2):
        pass

    @staticmethod
    def loop():
        tasks = Worker.collect_tasks()

        for task in tasks:
            task.status = 4
        db.session.commit()
        db.session.flush()

        for task in tasks:
            v = AmqpConnectionController()

            p = Pika()
            p.send_tasks(tasks)
            console_log("done sending")
        logging.info("looped")

    # @staticmethod
    # def nmap_to_resource(nmap_task):
    #     if not nmap_task:
    #         raise Exception("no nmap tasks")
    #
    #     nmap = Nmap()
    #     nmap_task.status = 1
    #     db.session.commit()
    #     db.session.flush()
    #
    #     now = datetime.now()
    #     scan_results = nmap.scan(nmap_task.rule)
    #     scan_time = (datetime.now() - now).total_seconds()
    #
    #     output = []
    #     for scan_result in scan_results:
    #         resource = None
    #         try:
    #             resource = ResourceController.get_resources(address=scan_result["host"],
    #                                                         port=scan_result["port"])
    #         except:
    #             pass
    #
    #         if not resource:
    #             if scan_result["service"] not in FileProtocols().get_names():
    #                 log_msg("Discovered service \"%s://%s:%d\" not regonized - should be any of: (%s)" % (
    #                     scan_result["service"],
    #                     scan_result["host"],
    #                     scan_result["port"],
    #                     ", ".join(FileProtocols().get_names())), level=1, author="taskloop")
    #                 continue
    #             else:
    #                 name = "%s_%s" % (nmap_task.name, random.randrange(10 ** 8))
    #                 try:
    #                     ResourceController.add_resource(
    #                         server_address=scan_result["host"],
    #                         resource_port=scan_result["port"],
    #                         resource_protocol=FileProtocols().id_by_name(scan_result["service"]),
    #                         server_name=name,
    #                         description="Discovered via nmap",
    #                         display_url="/",
    #                         recursive_sizes=True,
    #                         throttle_connections=-1,
    #                         current_user=0
    #                     )
    #                 except Exception as ex:
    #                     log_msg("Could not auto-add resource (%s:%d) with name \"%s\": %s" % (
    #                         name, scan_result["host"], scan_result["port"], str(ex)
    #                     ), level=2, author="taskloop")
    #                     continue
    #
    #                 log_msg("Discovered service \"%s://%s:%d\" - auto-adding as \"%s\"" % (
    #                     scan_result["service"],
    #                     scan_result["host"],
    #                     scan_result["port"],
    #                     name), author="taskloop")
    #         output.append(scan_result)
    #
    #     nmap_task.status = 0
    #     nmap_task.date_scanned = datetime.now()
    #     nmap_task.output["data"] = {
    #         "output": output,
    #         "time": scan_time
    #     }
    #     db.session.commit()
    #     db.session.flush()

    @staticmethod
    def collect_tasks(check_resources: bool = True, check_nmap: bool = True):
        tasks = {
            "nmap": [],
            "resources": []
        }
        if check_nmap:
            for nmap_rule in db.session.query(NmapRule).all():
                def _skipping(_rule):
                    log_msg("skipping nmap rule \'%s\': %s" % (_rule.name, _rule.rule), level=1)

                if isinstance(nmap_rule.crawl_interval, int) and isinstance(nmap_rule.date_scanned, datetime):
                    # check last scan time
                    if (datetime.now() - nmap_rule.date_scanned).total_seconds() <= nmap_rule.scan_interval:
                        _skipping(nmap_rule)
                        continue
                elif isinstance(nmap_rule.group.crawl_interval, int) and isinstance(nmap_rule.date_scanned, datetime):
                    if (datetime.now() - nmap_rule.date_scanned).total_seconds() <= nmap_rule.group.scan_interval:
                        _skipping(nmap_rule)
                        continue

                # continue when already 'busy'
                if nmap_rule.status != 0:
                    _skipping(nmap_rule)

                log_msg("adding nmap rule for scanning \'%s\': %s" % (
                    nmap_rule.name, nmap_rule.rule), author="taskloop")
                tasks["nmap"].append(nmap_rule)

        if check_resources:
            for group in db.session.query(ResourceGroup).all():
                crawl_interval = group.crawl_interval

                for resource in group.resources:
                    # check last crawl time
                    last = resource.date_crawl_end
                    if isinstance(last, datetime):
                        if (datetime.now() - last).total_seconds() <= crawl_interval:
                            continue

                    # continue when already 'busy'
                    if resource.meta.status != 0:
                        continue

                    tasks["resources"].append(resource)
                    log_msg("adding resource \'%s://%s\' (id: %d) for scanning" % (
                        resource.protocol_human, resource.resource_id, resource.id), author="taskloop")
        return tasks
    

class Nmap(NmapScan):
    def __init__(self):
        super(Nmap, self).__init__()

    def log_error(self, msg: str):
        log_msg(msg, 2)


worker = Worker()
worker.loop()