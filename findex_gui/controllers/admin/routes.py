from flask import request, redirect, url_for

from findex_gui.web import app, themes
from findex_gui.controllers.resources.resources import ResourceController
from findex_gui.controllers.amqp.forms import FormAmqpAdd
from findex_gui.controllers.user.decorators import admin_required


#
# general
#

@app.route("/admin")
@admin_required
def admin_home():
    from findex_gui.controllers.admin.status_report import AdminStatusReport
    blob = AdminStatusReport.status()
    return themes.render("main/home", theme="_admin", data=blob)

@admin_required
def admin_appearance():
    return themes.render("main/appearance", theme="_admin")

#
# AMQP
#

@app.route("/admin/amqp/overview")
@admin_required
def admin_amqp_list():
    return themes.render("main/amqp", theme="_admin")

@app.route("/admin/amqp/add")
@admin_required
def admin_amqp_add():
    amqp_add = FormAmqpAdd(request.form)
    return themes.render("main/amqp_add", theme="_admin", form_add=amqp_add)
