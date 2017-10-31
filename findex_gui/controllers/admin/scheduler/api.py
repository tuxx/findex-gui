from datetime import datetime, timedelta

import dateutil.parser
from flask_yoloapi import endpoint
from findex_common.utils_time import TimeMagic

from findex_gui.web import app, db
from findex_gui.orm.models import Crawler
from findex_gui.controllers.tasks.loop import Worker
from findex_gui.controllers.user.decorators import admin_required
from findex_gui.controllers.admin.scheduler.cron import CronController
from findex_gui.controllers.options.options import OptionsController
from findex_gui.controllers.admin.status.status import AdminStatusController

@app.route("/api/v2/admin/scheduler/cron_add")
@admin_required
@endpoint.api()
def api_admin_scheduler_cron_add():
    if CronController.has_cronjob():
        return "cron previously added"

    cron = CronController.generate_cronjob()
    CronController.insert_cronjob(cron)
    return "added"

@app.route("/api/v2/admin/scheduler/cron_remove")
@admin_required
@endpoint.api()
def api_admin_scheduler_cron_remove():
    if not CronController.has_cronjob():
        return "cron previously removed"

    CronController.remove_cronjob()
    return "removed"


@app.route("/api/v2/admin/scheduler/fire")
@admin_required
@endpoint.api()
def api_admin_scheduler_fire():
    worker = Worker()
    worker.loop()
    return True


@app.route("/api/v2/admin/scheduler/info")
@admin_required
@endpoint.api()
def api_admin_scheduler_last_ran():
    rtn = {}
    val = OptionsController.get("scheduler_last_ran")
    if not val:
        return None
    try:
        dt = dateutil.parser.parse(val.val["date"])
        rtn["last_ran"] = TimeMagic().ago_dt(dt)
    except:
        pass

    after = datetime.now() - timedelta(seconds=12)
    rtn["active_crawlers"] = len(db.session.query(Crawler).filter(Crawler.heartbeat >= after).all())
    return rtn
