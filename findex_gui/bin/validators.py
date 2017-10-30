import importlib

from findex_common.static_variables import FileProtocols

from findex_gui.orm.models import BASE

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

def server_group(value):
    from findex_gui.controllers.resources.groups import ResourceGroupController

    result = ResourceGroupController.get(name=value)
    if not result:
        raise Exception("resource group by the name \'%s\' does not exist" % value)

def strong_password(value):
    """better than nothing ;>"""
    min_length = 6
    if len(value) <= min_length:
        raise Exception("Password length must be %d characters or more" % min_length)

def valid_column(value):
    """Introspects SQLa class - checks for column_name"""
    try:
        model_name, column_name = value.split(":", 1)
    except:
        raise Exception("invalid input")

    try:
        module = importlib.import_module("findex_gui.orm.models")
        dmodule = dir(module)
        if model_name not in dmodule:
            raise Exception()
        model = getattr(module, model_name)
        if not issubclass(model, BASE):
            raise Exception()
        columns = [c.name for c in model.get_columns()]
    except:
        raise Exception("database table not found by the name \"%s\"" % model_name)
    try:
        if column_name not in columns:
            raise Exception()
    except:
        raise Exception("column name \"%s\" not found" % column_name)
