from findex_common.static_variables import FileProtocols

def amqp_broker(value):
    if value not in ["rabbitmq"]:
        raise Exception("unknown broker: %s" % value)

def server_protocol(value):
    if isinstance(value, str):
        protocol_names = FileProtocols().get_names()
        if value not in protocol_names:
            raise Exception("unknown protocol name '%s', available: %s" % (value, ",".join(protocol_names)))
    elif isinstance(value, int):
        protocol_ids = FileProtocols().data.values()
        if value not in protocol_ids:
            raise Exception("unkknown protocol id '%d', available: %s" % (value, map(str, protocol_ids)))

def strong_password(value):
    """better than nothing ;>"""
    min_length = 6
    if len(value) <= min_length:
        raise Exception("Password length must be %d characters or more" % min_length)
