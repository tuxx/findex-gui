from flask import request, redirect, url_for

from findex_gui.web import app, themes
from findex_gui.controllers.resources.resources import ResourceController
from findex_gui.controllers.user.decorators import admin_required
from findex_gui.controllers.admin.amqp.forms import FormMqAdd

@app.route("/admin/mq/overview")
@admin_required
def admin_mq_overview():
    return themes.render("main/mq/overview", theme="_admin")

@app.route("/admin/mq/add")
@admin_required
def admin_mq_add():
    mq_add = FormMqAdd(request.form)
    return themes.render("main/mq/add", theme="_admin",
                         form_add=mq_add)
