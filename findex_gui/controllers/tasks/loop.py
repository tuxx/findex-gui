from datetime import datetime

from findex_common.nmap import NmapScan

from findex_gui.web import db
from findex_gui.bin.utils import log_msg
from findex_gui.orm.models import NmapRule, ResourceGroup, Resource
from findex_gui.controllers.amqp.amqp import AmqpConnectionController
from findex_gui.controllers.tasks.crawler import Crawler


class Worker:
    @staticmethod
    def loop():
        tasks = Worker.collect_tasks()
        scheduled_resources = []

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

                    added_resources = nmap.nmap_to_resource(task, scan_results)
                    for added_resource in added_resources:
                        scheduled_resources.append(added_resource)
                elif isinstance(task, Resource):
                    scheduled_resources.append(task)

        if scheduled_resources:
            Crawler.spawn(scheduled_resources)

        log_msg("Scheduler loop finished", level=1)

    @staticmethod
    def collect_tasks(check_resources: bool = True, check_nmap: bool = True):
        tasks = []

        def _skipping(_task, level=1):
            if isinstance(_task, NmapRule):
                log_msg("skipping nmap rule \'%s\': %s" % (_task.name,
                                                           _task.rule), level=level)
            elif isinstance(_task, Resource):
                log_msg("skipping resource id: %d - \'%s\' [%s]" % (_task.id,
                                                                    _task.resource_id,
                                                                    _task.protocol_human.upper()), level=level)
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
                    # check last crawl time
                    last = resource.date_crawl_end
                    if isinstance(last, datetime):
                        if (datetime.now() - last).total_seconds() <= crawl_interval:
                            _skipping(resource, level=0)
                            continue

                    if resource.meta.status != 0:
                        _skipping(resource, level=0)
                        continue

                    tasks.append(resource)
                    resource.meta.status = 4  # task scheduled
                    log_msg("scheduled resource \'%s://%s\' (id: %d) for scanning" % (resource.protocol_human,
                                                                                      resource.resource_id, resource.id))
                db.session.commit()
                db.session.flush()
        return tasks

