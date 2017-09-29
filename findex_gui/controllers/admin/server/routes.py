from flask import request, redirect, url_for

from findex_gui.web import app, themes
from findex_gui.controllers.resources.resources import ResourceController
from findex_gui.controllers.user.decorators import admin_required
from findex_gui.controllers.admin.server.forms import FormServerAdd, FormServerAddOptions, FormServerAddAuthentication
from findex_gui.controllers.nmap.forms import NmapRuleAdd

@app.route("/admin/server/overview")
@admin_required
def admin_servers():
    return themes.render("main/server/overview", theme="_admin")

@app.route("/admin/server/add")
@admin_required
def admin_server_add():
    server_add = FormServerAdd(request.form)
    server_options = FormServerAddOptions(request.form)
    server_auth = FormServerAddAuthentication(request.form)
    return themes.render("main/server/add", theme="_admin",
                         form_add=server_add,
                         form_auth=server_auth,
                         form_options=server_options)

@app.route("/admin/server/<path:server_id>")
@admin_required
def admin_server_edit(server_id):
    return themes.render("main/server/edit", theme="_admin")

@app.route("/admin/server/remove/<browse:args>")
@admin_required
def admin_server_remove(args):
    resource, f, path, filename = args
    try:
        ResourceController.remove_resource(resource.id, auto_remove_server=True)
    except:
        return "Something went wrong while removing the server", 500
    return redirect(url_for("admin_servers"), 302)

#
# nmap
#

@app.route("/admin/server/nmap/add")
@admin_required
def admin_server_add_nmap():
    nmap_rule_add = NmapRuleAdd(request.form)
    return themes.render("main/server/add_nmap", theme="_admin", form_nmap_rule_add=nmap_rule_add)