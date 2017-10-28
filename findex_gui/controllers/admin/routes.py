from flask import request, redirect, url_for

from findex_gui.web import app, themes
from findex_gui.bin.misc import version
from findex_gui.controllers.admin.status.status import AdminStatusController
from findex_gui.controllers.amqp.forms import FormAmqpAdd
from findex_gui.controllers.user.decorators import admin_required
from findex_gui.controllers.news.news import NewsController


#
# general
#

@app.route("/admin")
@admin_required
def admin_home():
    return themes.render("main/home", theme="_admin", version=version)

@admin_required
def admin_appearance():
    return themes.render("main/appearance", theme="_admin")

#
# News
#

@app.route("/admin/news/overview")
@admin_required
def admin_news():
    posts = NewsController.get(limit=10)
    return themes.render("main/news/overview", theme="_admin", posts=posts)


@app.route("/admin/news/add")
@admin_required
def admin_news_add():
    return themes.render("main/news/edit_add", theme="_admin")

@app.route("/admin/news/edit/<path:uid>")
@admin_required
def admin_news_edit(uid):
    if not uid.isdigit():
        raise Exception("uid must be an integer")
    post = NewsController.get(uid=int(uid))
    return themes.render("main/news/edit_add", theme="_admin", post=post)

@app.route("/admin/news/remove/<path:uid>")
@admin_required
def admin_news_remove(uid):
    if not uid.isdigit():
        raise Exception("uid must be an integer")
    NewsController.remove(uid=int(uid))
    return redirect(url_for("admin_news"))

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
