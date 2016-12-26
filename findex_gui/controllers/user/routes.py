from flask import request, redirect, flash, url_for
from flaskext.auth.auth import get_current_user_data
from flask.ext.babel import gettext
from wtforms import Form, BooleanField, StringField, PasswordField, validators, SelectField, IntegerField

from findex_gui import app, themes, locales
from findex_gui.controllers.user.decorators import login_required
from findex_gui.controllers.user.user import UserController
from findex_gui.controllers.helpers import redirect_url
from findex_gui.controllers.resources.forms import ResourceForm


@app.route('/user/register', methods=['GET', 'POST'])
def register():
    return themes.render('main/register')


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


@app.route('/user/cp')
@login_required
def user_cp():
    form = LocalizationForm(request.form)
    form.language.choices = locales.items()
    form.language.data = UserController.locale_get()
    return themes.render('main/user_cp/_misc', form=form)


@app.route('/user/cp/services', methods=['GET'])
@login_required
def user_cp_resources():
    form = ResourceForm(request.form)
    return themes.render('main/user_cp/_services', form=form)


@app.route('/user/cp/services/add', methods=['GET'])
@login_required
def user_cp_resource_add():
    form = ResourceForm(request.form)
    return themes.render('main/user_cp/_service_add', form=form)


@app.route('/user/cp/services/<path:resource_id>', methods=['GET'])
@login_required
def user_cp_resource_detail(resource_id):
    # @TODO redo
    from findex_gui.controllers.resources.resources import ResourceController
    from findex_gui.orm.models import Resource
    from findex_gui import db
    try:
        resource = db.session.query(Resource).filter(Resource.id == resource_id).first()
    except:
        db.session.rollback()
        return "error"

    if not resource or isinstance(resource, Exception):
        raise Exception("None found")
    return themes.render('main/user_cp/_service_detail', resource=resource)


@app.route('/user/cp/services/<path:resource_id>/delete', methods=['GET'])
@login_required
def user_cp_resource_remove(resource_id):
    # @TODO redo
    from findex_gui.orm.models import Resource
    from findex_gui import db
    try:
        resource = db.session.query(Resource).filter(Resource.id == resource_id).first()
    except:
        db.session.rollback()
        return "error"

    if not resource or isinstance(resource, Exception):
        raise Exception("None found")

    from findex_gui.controllers.resources.resources import ResourceController
    ResourceController.remove_resource(resource_id=resource.id)
    return "nice"
