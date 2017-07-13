from flask import request, redirect, url_for

from findex_gui.web import app, themes
from findex_gui.bin.themes import render_template
from findex_gui.controllers.resources.resources import ResourceController
from findex_gui.controllers.user.decorators import admin_required


@admin_required
def admin_home():
    return themes.render("main/home", theme="_admin")


@admin_required
def admin_servers():
    return themes.render("main/servers", theme="_admin")


@admin_required
def admin_appearance():
    return themes.render("main/appearance", theme="_admin")


@admin_required
def admin_server_add():
    from findex_gui.controllers.admin.server_forms import FormServerAdd, FormServerAddOptions, \
        FormServerAddAuthentication

    server_add = FormServerAdd(request.form)
    server_options = FormServerAddOptions(request.form)
    server_auth = FormServerAddAuthentication(request.form)

    return themes.render("main/server_add", theme="_admin",
                         form_add=server_add,
                         form_auth=server_auth,
                         form_options=server_options)


@admin_required
def admin_server_edit(server_id):
    return themes.render("main/server_edit", theme="_admin")


def admin_server_remove(args):
    resource, f, path, filename = args
    try:
        ResourceController.remove_resource(resource.id, auto_remove_server=True)
    except:
        return "Something went wrong while removing the server", 500
    return redirect(url_for("admin_servers"), 302)


app.add_url_rule("/admin", view_func=admin_home)
app.add_url_rule("/admin/servers", view_func=admin_servers)
app.add_url_rule("/admin/server_add", view_func=admin_server_add)
app.add_url_rule("/admin/appearance", view_func=admin_appearance)
app.add_url_rule("/admin/server/<path:server_id>", view_func=admin_server_edit)
app.add_url_rule("/admin/server_remove/<browse:args>", view_func=admin_server_remove)
