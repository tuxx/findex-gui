from findex_gui import app, settings, themes
from flask import render_template
from findex_gui.controllers.user.decorators import admin_required


@admin_required
def admin_home():
    return render_template('_admin/templates/main/home.html')


@admin_required
def admin_servers():
    return render_template('_admin/templates/main/servers.html')


app.add_url_rule('/admin', view_func=admin_home)
app.add_url_rule('/admin/servers', view_func=admin_servers, endpoint='users')