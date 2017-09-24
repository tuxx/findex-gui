from flask_yoloapi import endpoint, parameter

from findex_gui.web import app
from findex_gui.bin import validators
from findex_gui.controllers.user.decorators import admin_required
from findex_gui.controllers.options.options import OptionsController

KEYS = [
    'theme_active',
]


@app.route("/api/v2/admin/server/test", methods=["POST"])
@admin_required
@endpoint.api(
    parameter("server_address", type=str, required=True),
    parameter("resource_port", type=int, required=True),
    parameter("resource_protocol", type=int, required=True, validator=validators.server_protocol),
    parameter("basepath", type=str, required=False, default="/"),
    parameter("auth_user", type=str, required=False),
    parameter("auth_pass", type=str, required=False),
    parameter("auth_type", type=str, required=False)
)
def api_admin_server_test_reachability(server_address, resource_port ,resource_protocol,
                                       auth_user, auth_pass, auth_type):
    """
    Test if server can be reached.
    :param server_name: Server name
    :param server_address: ipv4 'str' - clean hostname or IP
    :param server_id: server DB id
    :param resource_port: valid port number
    :param resource_protocol: valid protocol number 'int' - see `findex_common.static_variables.FileProtocols`
    :param basepath: the absolute crawl root path 'str'
    :param auth_user: resource user authentication 'str'
    :param auth_pass: resource pass authentication 'str'
    :param auth_type: resource type authentication 'str'
    :return:
    """
    from findex_gui.bin.reachability import TestReachability
    result = TestReachability.test(server_address, resource_port ,resource_protocol,
                                   auth_user, auth_pass, auth_type)
    return result


@app.route("/api/v2/admin/amqp/test", methods=["POST"])
@admin_required
@endpoint.api(
    parameter("name", type=str, required=True),
    parameter("address", type=str, required=True),
    parameter("port", type=int, required=True),
    parameter("broker", type=str, required=False, default= "rabbitmq", validator=validators.amqp_broker),
    parameter("user", type=str, required=True),
    parameter("passwd", type=str, required=True),
    parameter("vhost", type=str, required=True),
)
def api_admin_amqp_test_reachability(name, address, port, broker, user, password, vhost):
    """
    Test if AMQP can be reached.
    :param name: Name of the AMQP broker
    :param address: amqp server address
    :param port: amqp server port
    :param broker: rabbitmq or another type of message broker
    :param user: amqp user
    :param password: amqp pwd
    :param vhost: amqp vhost
    :return:
    """
    """verify address/port reachability"""
    from findex_gui.bin.reachability import TestReachability
    result = TestReachability.test(**data)
    return result


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
