import flask
from flask import request

from findex_gui.web import app, locales
from findex_gui.orm.models import User
from findex_gui.controllers.helpers import findex_api, ApiArgument as api_arg
from findex_gui.controllers.auth.auth import get_current_user_data
from findex_gui.controllers.user.decorators import login_required
from findex_gui.controllers.user.user import UserController


@app.route('/api/v2/user/locale', methods=['POST'])
def api_user_locale():
    e = ''


@app.route('/api/v2/user/locale/all', methods=['GET'])
def api_user_locale_available():
    return flask.jsonify(**locales)


@app.route('/api/v2/user/locale/set', methods=['POST'])
def api_user_locale_set():
    if "lang" in request.form:
        lang = request.form["lang"]
    elif "lang" in request.json:
        lang = request.json["lang"]
    else:
        return flask.jsonify(**{'fail': 'parameter \'lang\' not given'}), 400

    try:
        if request.authorization or get_current_user_data():
            if request.authorization:
                user = UserController.authenticate_basic()
            else:
                user = User.query.filter(
                    User.id == get_current_user_data()['id']).one()
            if user:
                UserController.locale_set(
                    locale=lang, user=user)
                return flask.jsonify(**{'success': True}), 201

        UserController.locale_set(locale=request.form['lang'])
        return flask.jsonify(**{'status': True}), 201
    except Exception as ex:
        return flask.jsonify(**{'fail': str(ex)}), 400


@app.route("/api/v2/user/delete", methods=["POST"])
@findex_api(
    api_arg("username", type=str, required=True, help="Username")
)
def api_user_delete(data):
    user = UserController.user_delete(username=data['username'])
    if isinstance(user, Exception):
        return user
    return data


@app.route("/api/v2/user/register", methods=["POST"])
@findex_api(
    api_arg("username", type=str, required=True, help="Username"),
    api_arg("password", type=str, required=True, help="Password")
)
def api_user_register(data):
    user = UserController.user_add(username=data['username'], password=data['password'])
    if isinstance(user, Exception):
        return user

    return "user registered"
