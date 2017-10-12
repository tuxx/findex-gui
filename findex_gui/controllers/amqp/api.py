from flask_yoloapi import endpoint, parameter

from findex_gui.web import app
from findex_gui.bin import validators
from findex_gui.controllers.user.decorators import admin_required
from findex_gui.controllers.amqp.amqp import MqController
from findex_gui.controllers.amqp.amqp import AmqpConnectionController


@app.route("/api/v2/admin/mq/add", methods=["POST"])
@admin_required
@endpoint.api(
    parameter("name", type=str, required=True),
    parameter("broker", type=str, required=True, default="rabbitmq", validator=validators.amqp_broker),
    parameter("host", type=str, required=True),
    parameter("port", type=int, required=True),
    parameter("vhost", type=str, required=True),
    parameter("queue", type=str, required=True),
    parameter("ssl", type=bool, required=False, default=False),
    parameter("auth_user", type=str, required=True),
    parameter("auth_pass", type=str, required=True),
)
def api_admin_mq_add(name, broker, host, port, vhost, queue, ssl, auth_user, auth_pass):
    """
    Adds a MQ server, for now, only rabbitmq is supported
    :param name: name of the 'mq' broker
    :param broker: broker type (rabbitmq, ...)
    :param host: 'mq' server address
    :param port: 'mq' server port
    :param vhost: 'mq' vhost
    :param queue: 'mq' queue name
    :param ssl: connect via SSL?
    :param auth_user: 'mq' user
    :param auth_pass: 'mq' pwd
    :return: mq
    """
    MqController.add(
        name=name, host=host, port=port, vhost=vhost,
        queue=queue, ssl=ssl, auth_user=auth_user, auth_pass=auth_pass)
    return True


@app.route("/api/v2/admin/mq/get", methods=["GET"])
@admin_required
@endpoint.api(
    parameter("uid", type=int, required=False),
    parameter("name", type=str, required=False),
    parameter("host", type=str, required=False),
    parameter("port", type=int, required=False),
    parameter("limit", type=int, default=10),
    parameter("offset", type=int, default=0),
    parameter("search", type=str, required=False, default=None)
)
def api_admin_mq_get(uid, name, host, port, limit, offset, search):
    """
    Gets a MQ broker
    :param uid: db row id
    :param name: name of the 'mq' broker
    :param host: 'mq' server address
    :param port: 'mq' server port
    :param limit:
    :param offset:
    :return: mq
    """
    args = {
        "limit": limit,
        "offset": offset
    }

    records = MqController.get(uid=uid, name=name, host=host, port=port,
                               limit=args['limit'], offset=args['offset'])

    # bleh
    args.pop('limit')
    args.pop('offset')
    total = MqController.get(uid=uid, name=name, host=host, port=port)

    return {
        "records": records,
        "queryRecordCount": len(total),
        "totalRecordCount": len(records)
    }


@app.route("/api/v2/admin/amqp/test", methods=["POST"])
@admin_required
@endpoint.api(
    parameter("broker", type=str, required=True, default="rabbitmq", validator=validators.amqp_broker),
    parameter("host", type=str, required=True),
    parameter("port", type=int, required=True),
    parameter("vhost", type=str, required=True),
    parameter("queue", type=str, required=True),
    parameter("ssl", type=bool, required=False, default=False),
    parameter("auth_user", type=str, required=True),
    parameter("auth_pass", type=str, required=True)
)
def api_admin_mq_test(broker, host, port, vhost, queue, ssl, auth_user, auth_pass):
    """
    Test if a MQ broker can be reached.
    :param host: 'mq' server address
    :param port: 'mq' server port
    :param broker: rabbitmq or another type of message broker
    :param auth_user: 'mq' user
    :param auth_pass: 'mq' pwd
    :param vhost: 'mq' vhost
    :return:
    """
    if broker == "rabbitmq":
        return AmqpConnectionController.test_amqp(auth_user, auth_pass, host, vhost, queue, port)

