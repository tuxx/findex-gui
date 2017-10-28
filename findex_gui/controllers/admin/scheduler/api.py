import dateutil.parser
from flask_yoloapi import endpoint
from findex_common.utils_time import TimeMagic

from findex_gui.web import app
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


@app.route("/api/v2/admin/scheduler/last_ran")
@admin_required
@endpoint.api()
def api_admin_scheduler_last_ran():
    val = OptionsController.get("scheduler_last_ran")
    if not val:
        return None
    try:
        dt = dateutil.parser.parse(val.val["date"])
        return TimeMagic().ago_dt(dt)
    except:
        pass
