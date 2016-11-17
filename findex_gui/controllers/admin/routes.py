from findex_gui import app, settings, themes
from flask import render_template
from findex_gui.controllers.user.decorators import admin_required


@admin_required
def admin_home():
    return render_template('main/home', theme="_admin")


@admin_required
def admin_servers():
    return themes.render('main/servers', theme="_admin")


app.add_url_rule('/admin', view_func=admin_home)
app.add_url_rule('/admin/servers', view_func=admin_servers)