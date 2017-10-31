from findex_gui.web import app
from findex_gui.controllers.user.decorators import admin_required
from findex_gui.controllers.admin.status.status import AdminStatusController

from flask_yoloapi import endpoint

@app.route("/api/v2/admin/status/errors")
@admin_required
@endpoint.api()
def api_admin_status_errors():
    errors, checked = AdminStatusController.has_errors()
    return {
        "errors": len(errors),
        "checked": checked,
        "ok": checked - len(errors)
    }
