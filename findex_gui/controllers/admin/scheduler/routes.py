from findex_gui.web import app, themes
from findex_gui.controllers.user.decorators import admin_required
from findex_gui.controllers.admin.scheduler.cron import CronController


@app.route("/admin/scheduler/overview")
@admin_required
def admin_scheduler_overview():
    has_cron = CronController.has_cronjob()
    generated_cron = CronController.generate_cronjob()
    return themes.render("main/scheduler/overview", theme="_admin",
                         has_cron=has_cron,
                         generated_cron=generated_cron)
