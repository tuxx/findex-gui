from findex_gui.web import app
from findex_gui.bin.api import FindexApi, api_arg
from findex_gui.controllers.user.decorators import admin_required
from findex_gui.controllers.options.options import OptionsController

KEYS = [
    'theme_active',
]


@app.route("/api/v2/admin/option_get", methods=["POST"])
@admin_required
@FindexApi(
    api_arg("key", type=str, required=True, help="a key is required")
)
def api_admin_option_get(data):
    global KEYS

    controller = OptionsController.get(data["key"])
    if controller:
        return controller.val
    return Exception("Unknown key \'%s\'" % data["key"])


@app.route("/api/v2/admin/server/test", methods=["POST"])
@admin_required
@FindexApi(
    api_arg("address", type=str, required=True, help="Address"),
    api_arg("port", type=int, required=True, help="Port"),
    api_arg("protocol", type=int, required=True, help="Protocol"),
    api_arg("user", type=str, required=False, help="User"),
    api_arg("pwd", type=str, required=False, help="Pwd"),
    api_arg("auth_type", type=str, required=False, help="Auth type"),
)
def api_admin_server_test_reachability(data):
    """verify address/port reachability"""
    from findex_gui.bin.reachability import TestReachability
    result = TestReachability.test(**data)
    return result


@app.route("/api/v2/admin/amqp/test", methods=["POST"])
@admin_required
@FindexApi(
    api_arg("name", type=str, required=True, help="Name of the AMQP broker"),
    api_arg("address", type=str, required=True, help="Address"),
    api_arg("port", type=int, required=True, help="Port"),
    api_arg("broker", type=str, required=True, help="The AMQP broker, default: rabbitmq"),
    api_arg("user", type=str, required=True, help="User"),
    api_arg("passwd", type=str, required=True, help="Pwd"),
    api_arg("vhost", type=str, required=True, help="Pwd"),
)
def api_admin_amqp_test_reachability(data):
    """verify address/port reachability"""
    from findex_gui.bin.reachability import TestReachability
    result = TestReachability.test(**data)
    return result


@app.route("/api/v2/admin/option_set", methods=["POST"])
@admin_required
@FindexApi(
    api_arg("key", type=str, required=True, help="Key is required"),
    api_arg("val", type=str, required=True, help="Value is required")
)
def api_admin_option_set(data):
    global KEYS

    if data["key"] not in KEYS:
        return "Unknown key \'%s\'" % data["key"]

    OptionsController.set(key=data["key"], val=data["val"])
    return "key set"
