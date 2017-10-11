from flask import request, redirect, url_for

from findex_gui.web import app, themes
from findex_gui.controllers.resources.resources import ResourceController
from findex_gui.controllers.user.decorators import admin_required
from findex_gui.controllers.nmap.forms import NmapRuleAdd

@app.route("/admin/mq/overview")
@admin_required
def admin_mqs():
    return themes.render("main/mq/overview", theme="_admin")
#
# @app.route("/admin/mq/add")
# @admin_required
# def admin_mq_add():
#     mq_add = FormServerAdd(request.form)
#     mq_options = FormServerAddOptions(request.form)
#     mq_auth = FormServerAddAuthentication(request.form)
#     return themes.render("main/mq/add", theme="_admin",
#                          form_add=mq_add,
#                          form_auth=mq_auth,
#                          form_options=mq_options)
#
# @app.route("/admin/mq/<path:mq_id>")
# @admin_required
# def admin_mq_edit(mq_id):
#     return themes.render("main/mq/edit", theme="_admin")
#
# @app.route("/admin/mq/remove/<browse:args>")
# @admin_required
# def admin_mq_remove(args):
#     resource, f, path, filename = args
#     try:
#         ResourceController.remove_resource(resource.id, auto_remove_mq=True)
#     except:
#         return "Something went wrong while removing the mq", 500
#     return redirect(url_for("admin_mqs"), 302)
#
# #
# # nmap
# #
#
# @app.route("/admin/mq/nmap/add")
# @admin_required
# def admin_mq_add_nmap():
#     nmap_rule_add = NmapRuleAdd(request.form)
#     return themes.render("main/mq/add_nmap", theme="_admin", form_nmap_rule_add=nmap_rule_add)
