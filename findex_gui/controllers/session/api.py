from flask import session
from flask_yoloapi import endpoint, parameter

from findex_gui.web import app

KEYS = [
    "search_display_view"
]

VALUES = [
    "table", "fancy"
]


@app.route("/api/v2/session/set", methods=["POST"])
@endpoint.api(
    parameter("key", type=str, required=True),
    parameter("val", type=str, required=False)
)
def api_session_set(key, val):
    if key not in KEYS:
        return Exception("key \"%s\" doesn't exist" % key)
    if val not in VALUES:
        return Exception("could not set val \"%s\" - doesn't exist" % val)
    session[key] = val
    return "session key set"


@app.route("/api/v2/session/get", methods=["POST"])
@endpoint.api(
    parameter("key", type=str, required=True),
    parameter("val", type=str, required=True)
)
def api_session_get(key, val):
    if key not in KEYS:
        return Exception("key \"%s\" doesn't exist" % key)
    if key not in session:
        session[key] = "fancy"
    return session[key]
