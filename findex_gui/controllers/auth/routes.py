from flask import request, redirect, flash, url_for

from findex_gui import app, db, themes
from findex_gui.orm.models import Users
from findex_gui.controllers.auth.auth import AuthController
from findex_gui.controllers.helpers import redirect_url
from flaskext.auth.auth import get_current_user_data


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if AuthController().register(username, password):
            return redirect(redirect_url())
        else:
            return themes.render('main/register', error="Error while registering")

    return themes.render('main/register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if get_current_user_data():
        return 'user already logged in'

    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if AuthController().login(username, password):
            flash('You were successfully logged in')
            if request.referrer.endswith('/login'):
                return redirect(url_for('.root'))

            return redirect(redirect_url())
        else:
            error = 'Invalid credentials'

    return themes.render('main/login', error=error)