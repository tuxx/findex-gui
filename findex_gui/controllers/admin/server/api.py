from flask_yoloapi import endpoint, parameter

from findex_gui.web import app
from findex_gui.bin import validators
from findex_gui.bin.reachability import TestReachability
from findex_gui.controllers.user.decorators import admin_required

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
def api_admin_server_test_reachability(server_address, basepath,
                                       resource_port, resource_protocol,
                                       auth_user, auth_pass, auth_type):
    """
    Test if server can be reached.
    :param server_address: ipv4 'str' - clean hostname or IP
    :param resource_port: valid port number
    :param resource_protocol: valid protocol number 'int' - see `findex_common.static_variables.FileProtocols`
    :param basepath: the absolute crawl root path 'str'
    :param auth_user: resource user authentication 'str'
    :param auth_pass: resource pass authentication 'str'
    :param auth_type: resource type authentication 'str'
    :return:
    """
    result = TestReachability.test(server_address, resource_port, resource_protocol,
                                   basepath, auth_user, auth_pass, auth_type)
    return result
