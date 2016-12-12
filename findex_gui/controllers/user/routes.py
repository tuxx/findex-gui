from flask import request, redirect, flash, url_for
from flaskext.auth.auth import get_current_user_data
from flask.ext.babel import gettext
from wtforms import Form, BooleanField, StringField, PasswordField, validators, SelectField

from findex_gui import app, themes, locales
from findex_gui.controllers.user.decorators import login_required
from findex_gui.controllers.user.user import UserController
from findex_gui.controllers.helpers import redirect_url


# @app.route('/user/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#
#         user = UserController.user_add(username, password)
#         if isinstance(user, Exception):
#             return themes.render('main/register', error=str(user))
#         else:
#             return redirect('/')
#
#     return themes.render('main/register')


@app.route('/user/login', methods=['GET', 'POST'])
def login():
    if get_current_user_data():
        return redirect('/', 302)

    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if UserController.authenticate_and_session(username, password):
            flash(gettext('You were successfully logged in'))
            if request.referrer.endswith('/login'):
                return redirect(url_for('root'))

            return redirect(redirect_url())
        else:
            error = gettext('Invalid credentials')

    return themes.render('main/login', error=error)


@app.route('/user/logout', methods=['GET'])
def logout():
    if not get_current_user_data():
        return redirect_url('login')

    UserController.logout()

    return redirect('/', 302)


class LocalizationForm(Form):
    language = SelectField('Language', choices=[], coerce=str)


@app.route('/user/cp', methods=['GET'])
@login_required
def user_cp():

    form = LocalizationForm(request.form)
    form.language.choices = locales.items()
    form.language.data = UserController.locale_get()

    return themes.render('main/user_cp', form=form)
