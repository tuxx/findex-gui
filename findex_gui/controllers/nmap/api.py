from flask import jsonify
from flask_yoloapi import endpoint, parameter
from sqlalchemy import func

from findex_gui.web import app, db
from findex_gui.orm.models import NmapRule
from findex_gui.controllers.user.decorators import admin_required
from findex_gui.controllers.nmap.nmap import NmapController

@app.route("/api/v2/admin/server/nmap/add", methods=["POST"])
@admin_required
@endpoint.api(
    parameter("rule", type=str, required=True),
    parameter("name", type=str, required=True),
    parameter("interval", type=str, required=False, default=None),
)
def api_admin_server_nmap_add(rule, name, interval):
    if isinstance(interval, str) and not interval.isdigit():
        interval = None
    return NmapController.add(cmd=rule, name=name, interval=interval)

@app.route("/api/v2/admin/server/nmap/delete", methods=["POST"])
@admin_required
@endpoint.api(
    parameter("uid", type=int, required=True)
)
def api_admin_server_nmap_remove(uid):
    return NmapController.remove(uid)

@app.route("/api/v2/admin/server/nmap/get", methods=["GET"])
@endpoint.api(
    parameter("uid", type=str, required=False),
    parameter("limit", type=int, default=10),
    parameter("offset", type=int, default=0)
)
def api_admin_server_nmap_get(uid, limit, offset):
    """
    Get nmap rules.
    :param uid: nmap uid
    :param limit:
    :param offset:
    :return: nmap_rule object
    """
    args = {
        "limit": limit,
        "offset": offset
    }
    if isinstance(uid, str) and uid:
        args["uid"] = uid

    scan_results = NmapController.get(**args)
    record_count = db.session.query(func.count(NmapRule.id)).scalar()

    return {
        "records": scan_results,
        "queryRecordCount": record_count,
        "totalRecordCount": len(scan_results)
    }
