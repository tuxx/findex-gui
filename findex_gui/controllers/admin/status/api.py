from findex_gui.web import app

from flask_yoloapi import endpoint

from findex_gui.controllers.admin.status.status import AdminStatusController

@app.route("/api/v2/admin/status/errors")
@endpoint.api()
def api_admin_status_errors():
    errors, checked = AdminStatusController.has_errors()
    return {
        "errors": len(errors),
        "checked": checked,
        "ok": checked - len(errors)
    }
