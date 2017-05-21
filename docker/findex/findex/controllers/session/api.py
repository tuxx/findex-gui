import flask
from flask import session

from findex_gui.web import app
from findex_gui.controllers.helpers import findex_api, ApiArgument as api_arg

KEYS = [
    "search_display_view"
]

VALUES = [
    "table", "fancy"
]


@app.route("/api/v2/session/set", methods=["POST"])
@findex_api(
    api_arg("key", type=str, required=True, help="key is required"),
    api_arg("val", type=str, required=False, help="value")
)
def api_session_set(data):
    key = data["key"]
    val = data["val"]

    if key not in KEYS:
        return Exception("key \"%s\" doesn't exist" % key)

    if val not in VALUES:
        return Exception("could not set val \"%s\" - doesn't exist" % val)

    session[key] = val
    return "session key set"


@app.route("/api/v2/session/get", methods=["POST"])
@findex_api(
    api_arg("key", type=str, required=True, help="key is required"),
    api_arg("val", type=str, required=True, help="value is required")
)
def api_session_get(data):
    key = data["key"]

    if key not in KEYS:
        return Exception("key \"%s\" doesn't exist" % key)

    if key not in session:
        session[key] = "fancy"

    return session[key]
