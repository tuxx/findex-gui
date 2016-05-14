from findex_gui import app, settings, themes
from flask import render_template
from flaskext.auth import Auth, AuthUser, login_required, logout


@app.route('/admin')
@login_required()
def admin():
    return render_template('_admin/templates/main/home.html')