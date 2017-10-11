from flask_yoloapi import endpoint, parameter

from findex_gui.web import app
from findex_gui.bin import validators
from findex_gui.controllers.user.decorators import admin_required
from findex_gui.controllers.amqp.amqp import AmqpController


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
    result = TestReachability.test(name=name, port=port)
    return result
