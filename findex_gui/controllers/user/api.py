import flask
from flask import request

from findex_gui.web import app, locales
from findex_gui.orm.models import User
from findex_gui.bin.api import FindexApi, api_arg
from findex_gui.controllers.auth.auth import get_current_user_data
from findex_gui.controllers.user.decorators import login_required
from findex_gui.controllers.user.user import UserController


@app.route("/api/v2/user/locale", methods=["POST"])
def api_user_locale():
    e = ""


@app.route("/api/v2/user/locale/all", methods=["GET"])
def api_user_locale_available():
    return flask.jsonify(**locales)


@app.route("/api/v2/user/locale/set", methods=["POST"])
@FindexApi(
    api_arg("lang", type=str, required=True, help="The language as \"en\" or \"nl\", etc.")
)
def api_user_locale_set(data):
    """
    Sets the web interface locale.
    :return:
    """
    lang = data.get("lang")

    try:
        current_user = get_current_user_data()
        if get_current_user_data():
            UserController.locale_set(locale=lang, user_id=current_user["id"])
            return True

        UserController.locale_set(locale=lang)
        return True
    except Exception as ex:
        return ex


@app.route("/api/v2/user/delete", methods=["POST"])
@FindexApi(
    api_arg("username", type=str, required=True, help="Username")
)
def api_user_delete(data):
    user = UserController.user_delete(username=data["username"])
    if isinstance(user, Exception):
        return user
    return data


@app.route("/api/v2/user/register", methods=["POST"])
@FindexApi(
    api_arg("username", type=str, required=True, help="Username"),
    api_arg("password", type=str, required=True, help="Password")
)
def api_user_register(data):
    user = UserController.user_add(username=data["username"], password=data["password"])
    if isinstance(user, Exception):
        return user

    return "user registered"
