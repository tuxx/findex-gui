from flask_yoloapi import endpoint, parameter
from findex_common.utils_time import TimeMagic

from findex_gui.web import app
from findex_gui.controllers.user.decorators import admin_required
from findex_gui.controllers.admin.logs.logs import LogController

@app.route("/api/v2/admin/logs/get")
@admin_required
@endpoint.api(
    parameter("category", type=str),
    parameter("limit", type=int, default=10),
    parameter("offset", type=int, default=0)
)
def api_admin_scheduler_logs_get(category, limit, offset):
    entries = LogController.get(category=category,
                                limit=limit,
                                offset=offset)

    rtn = []
    for entry in entries:
        blob = entry.get_json()
        blob["date_added_ago"] = TimeMagic().ago_dt(blob["date_added"])
        rtn.append(blob)

    return {
        "records": rtn,
        "totalRecordCount": len(rtn),
        "queryRecordCount": -1
    }
