from findex_gui.web import app
from findex_gui.controllers.helpers import findex_api, ApiArgument as api_arg
from findex_gui.controllers.user.decorators import admin_required
from findex_gui.controllers.options.options import OptionsController

KEYS = [
    'theme_active',
]


# @TODO: ADMIN REQUIRED ON THESE !!

@app.route("/api/v2/admin/option_get", methods=["POST"])
@findex_api(
    api_arg("key", type=str, required=True, help="a key is required")
)
def api_admin_option_get(data):
    global KEYS

    controller = OptionsController.get(data["key"])
    if controller:
        return controller.val
    return Exception("Unknown key \'%s\'" % data["key"])


@app.route("/api/v2/admin/option_set", methods=["POST"])
@findex_api(
    api_arg("key", type=str, required=True, help="Key is required"),
    api_arg("val", type=str, required=True, help="Value is required")
)
def api_admin_option_set(data):
    global KEYS

    if data["key"] not in KEYS:
        return "Unknown key \'%s\'" % data["key"]

    OptionsController.set(key=data["key"], val=data["val"])
    return flask.jsonify(**{"message": "key set"})
