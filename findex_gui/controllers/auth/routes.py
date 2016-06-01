from flask import request, redirect, flash, url_for
from flaskext.auth.auth import get_current_user_data
from flask.ext.babel import gettext

from findex_gui import app, db, themes
from findex_gui.orm.models import Users
from findex_gui.controllers.user.user import UserController
from findex_gui.controllers.helpers import redirect_url


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = UserController.register(username, password)

        if isinstance(user, Exception):
            return themes.render('main/register', error=str(user))
        else:
            return redirect(redirect_url())

    return themes.render('main/register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if get_current_user_data():
        return gettext('user already logged in')

    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if UserController.login(username, password):
            flash(gettext('You were successfully logged in'))
            if request.referrer.endswith('/login'):
                return redirect(url_for('.root'))

            return redirect(redirect_url())
        else:
            error = gettext('Invalid credentials')

    return themes.render('main/login', error=error)