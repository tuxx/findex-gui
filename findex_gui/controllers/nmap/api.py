from flask_yoloapi import endpoint, parameter

from findex_gui.web import app
from findex_gui.controllers.user.decorators import admin_required
from findex_gui.controllers.nmap.nmap import NmapController

@app.route("/api/v2/admin/server/nmap/add", methods=["POST"])
@admin_required
@endpoint.api(
    parameter("rule", type=str, required=True)
)
def api_admin_server_nmap_add(rule):
    return NmapController.add(rule)

@app.route("/api/v2/admin/server/nmap/delete", methods=["POST"])
@admin_required
@endpoint.api(
    parameter("uid", type=int, required=True)
)
def api_admin_server_nmap_remove(uid):
    return NmapController.remove(uid)
