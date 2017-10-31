import flask
from flask_yoloapi import endpoint, parameter

from findex_gui.web import app, locales
from findex_gui.bin import validators
from findex_gui.orm.models import User
from findex_gui.controllers.auth.auth import get_current_user_data
from findex_gui.controllers.user.decorators import login_required
from findex_gui.controllers.user.user import UserController


@app.route("/api/v2/user/delete", methods=["POST"])
@endpoint.api(
    parameter("username", type=str, required=True)
)
def api_user_delete(username):
    """
    Deletes an user.
    :param username: the username in question
    :return:
    """
    user = UserController.user_delete(username=username)
    return "user '%s' deleted" % username


@app.route("/api/v2/user/register", methods=["POST"])
@endpoint.api(
    parameter("username", type=str, required=True),
    parameter("password", type=str, required=True, validator=validators.strong_password)
)
def api_user_register(username, password):
    """
    Register a new user
    :param username: the username in question
    :param password: super secure password
    :return:
    """
    user = UserController.user_add(username=username, password=password)
    return "user '%s' registered" % username


@app.route("/api/v2/user/locale", methods=["POST"])
def api_user_locale():
    e = ""


@app.route("/api/v2/user/locale/all", methods=["GET"])
def api_user_locale_available():
    return locales


@app.route("/api/v2/user/locale/set", methods=["POST"])
@endpoint.api(
    parameter("lang", type=str, required=True)
)
def api_user_locale_set(lang):
    """
    Sets the web interface locale.
    :param lang: The language as "en" or "nl", etc.
    :return:
    """
    current_user = get_current_user_data()
    if get_current_user_data():
        UserController.locale_set(locale=lang, user_id=current_user["id"])
        return "locale set to %s" % lang

    UserController.locale_set(locale=lang)
    return "local set to %s" % lang
