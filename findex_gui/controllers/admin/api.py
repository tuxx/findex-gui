from flask_yoloapi import endpoint, parameter

from findex_gui.web import app
from findex_gui.bin import validators
from findex_gui.controllers.user.decorators import admin_required
from findex_gui.controllers.options.options import OptionsController

KEYS = [
    'theme_active',
]


@app.route("/api/v2/admin/option_set", methods=["POST"])
@admin_required
@endpoint.api(
    parameter("key", type=str, required=True),
    parameter("val", type=str, required=True)
)
def api_admin_option_set(key, val):
    global KEYS

    if key not in KEYS:
        raise Exception("Unknown key \'%s\'" % key)

    OptionsController.set(key=key, val=val)
    return "key set"


@app.route("/api/v2/admin/option_get", methods=["POST"])
@admin_required
@endpoint.api(
    parameter("key", type=str, required=True)
)
def api_admin_option_get(key):
    """
    Fetch an option
    """
    global KEYS

    controller = OptionsController.get(key)
    if controller:
        return controller.val
    return Exception("Unknown key \'%s\'" % key)
