import os
from datetime import datetime
from time import sleep
import random
import string
import json
import sys

import pika
from pika import credentials

import logging


def worker():
    import settings
    from findex_gui.web import db
    from findex_gui.orm.connect import Database
    from findex_gui.orm.models import ResourceGroup, NmapRule
    from findex_common.static_variables import FileProtocols
    from findex_gui.controllers.nmap.scan import nmap_scan
    from findex_gui.controllers.resources.resources import ResourceController

    tasks = {
        "crawls": [],
        "nmap": []
    }

    # for group in db.session.query(ResourceGroup).all():
    #     crawl_interval = group.interval
    #
    #     for resource in group.parents:
    #         # check last crawl time
    #         last = resource.date_crawl_end
    #         if isinstance(last, datetime):
    #             if (datetime.now() - last).total_seconds() <= crawl_interval:
    #                 continue
    #
    #         # continue when already 'busy'
    #         if resource.meta.status != 0:
    #             continue
    #
    #         tasks["crawls"].append(resource)
    #         resource.meta.status = 4  # amqp task sent
    #         logging.info("marked resource %d for crawl")

    for nmap_rule in db.session.query(NmapRule).all():
        if isinstance(nmap_rule.date_scanned, datetime):
            if (datetime.now() - nmap_rule.date_scanned).total_seconds() <= nmap_rule.scan_interval:
                pass

        tasks["nmap"].append(nmap_rule)

    # ------------

    if tasks["crawls"]:
        # db.session.commit()
        # db.session.flush()
        # p = Pika()
        # p.send_tasks(tasks)
        # console_log("done sending")
        pass

    if tasks["nmap"]:
        for scan in tasks["nmap"]:
            now = datetime.now()
            scan_results = nmap_scan(scan.rule)
            scan_time = (datetime.now() - now).total_seconds()

            output = []
            for scan_result in scan_results:
                resource = None
                try:
                    resource = ResourceController.get_resources(address=scan_result["host"], port=scan_result["port"])
                except Exception as ex:
                    pass

                if not resource:
                    if scan_result["service"] not in FileProtocols().get_names():
                        print("Discovered service \"%s://%s:%d\" not regonized - should be any of: (%s)" % (
                            scan_result["service"],
                            scan_result["host"],
                            scan_result["port"],
                            ", ".join(FileProtocols().get_names())
                        ))
                        continue

                    name = "%s_%s" % (scan.name, random.randrange(10**8))
                    ResourceController.add_resource(
                        server_address=scan_result["host"],
                        resource_port=scan_result["port"],
                        resource_protocol=FileProtocols().id_by_name(scan_result["service"]),
                        server_name=name,
                        description="Discovered via nmap",
                        display_url="/",
                        recursive_sizes=True,
                        throttle_connections=-1,
                        current_user=0
                    )

                output.append(scan_result)

            scan.date_scanned = datetime.now()
            scan.output["data"] = {
                "output": output,
                "time": scan_time
            }

            db.session.commit()
            db.session.flush()

    logging.info("looped")
