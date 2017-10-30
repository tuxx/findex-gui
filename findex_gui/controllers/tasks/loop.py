from datetime import datetime

from findex_common.nmap import NmapScan

from findex_gui.web import db
from findex_gui.bin.utils import log_msg
from findex_gui.orm.models import NmapRule, ResourceGroup, Resource
from findex_gui.controllers.options.options import OptionsController
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

        log_msg("Scheduler loop finished", level=1, category="scheduler")
        OptionsController.set("scheduler_last_ran", {"date": datetime.now().isoformat()})

    @staticmethod
    def collect_tasks(check_resources: bool = True, check_nmap: bool = True):
        log_msg("Collecting tasks", level=1, category="scheduler")
        skipped = {"nmap": 0, "resources": 0}
        tasks = []

        def _skipping(_task, level=1):
            if isinstance(_task, NmapRule):
                skipped["nmap"] += 1
            elif isinstance(_task, Resource):
                skipped["resources"] += 1

        if check_nmap:
            for nmap_rule in db.session.query(NmapRule).filter(NmapRule.status == 0):
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
                log_msg("scheduled nmap rule for scanning \'%s\': %s" % (nmap_rule.name, nmap_rule.rule),
                        category="scheduler")
            db.session.commit()
            db.session.flush()

        if check_resources:
            for group in db.session.query(ResourceGroup):
                for resource in group.resources:
                    if resource.meta.status != 0:
                        _skipping(resource, level=0)
                        continue

                    # check last crawl time
                    next_crawl = (datetime.now() - resource.date_crawl_next).total_seconds()
                    if next_crawl <= 0:
                        _skipping(resource, level=0)
                        continue

                    tasks.append(resource)
                    resource.meta.status = 4  # task scheduled
                    log_msg("scheduled resource \'%s://%s\' (id: %d) for scanning" % (
                        resource.protocol_human,
                        resource.resource_id, resource.id), category="scheduler")
                db.session.commit()
                db.session.flush()

        if skipped["nmap"] or skipped["resources"]:
            log_msg("skipping %d resource(s), %d nmap rule(s)" % (skipped["resources"], skipped["nmap"]),
                    category="scheduler", level=1)
        return tasks
