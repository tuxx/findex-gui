from flask_yoloapi import endpoint, parameter
from sqlalchemy import func

from findex_common.static_variables import FileProtocols
from findex_gui.web import app, db
from findex_gui.bin import validators
from findex_gui.bin.reachability import TestReachability
from findex_gui.orm.models import ResourceGroup
from findex_gui.controllers.amqp.amqp import MqController
from findex_gui.controllers.resources.resources import ResourceController
from findex_gui.controllers.resources.groups import ResourceGroupController
from findex_gui.controllers.user.decorators import admin_required

@app.route("/api/v2/resource/add", methods=["POST"])
@endpoint.api(
    parameter("server_name", type=str, required=False),
    parameter("server_address", type=str, required=False),
    parameter("server_id", type=int, required=False),

    parameter("resource_port", type=int, required=True),
    parameter("resource_protocol", type=int, required=False,
              validator=validators.server_protocol),

    parameter("auth_user", type=str, required=False),
    parameter("auth_pass", type=str, required=False),
    parameter("auth_type", type=str, required=False),

    parameter("user_agent", type=str, required=False),
    parameter("recursive_sizes", type=bool, required=False),

    parameter("basepath", type=str, required=True),
    parameter("display_url", type=str, required=False),
    parameter("description", type=str, required=False),
    parameter("throttle_connections", type=int, required=False),

    parameter("group", type=str, required=False, default="Default", validator=validators.server_group)
)
def api_resource_add_post(server_name, server_address, server_id, resource_port, resource_protocol, auth_user,
                          auth_pass, auth_type, user_agent, recursive_sizes, basepath, display_url, description,
                          throttle_connections, group):
    """
    Adds a local or remote file resource
    :param server_name: Server name
    :param server_address: ipv4 - clean hostname or IP
    :param server_id: server DB uid
    :param resource_port: valid port number
    :param resource_protocol: valid protocol number - see `findex_common.static_variables.FileProtocols`
    :param description: resource description
    :param display_url: url prefix as it will be shown on the front-end
    :param basepath: the absolute crawl root path
    :param recursive_sizes: recursively calculate directory sizes (performance impact during crawl)
    :param auth_user: resource user authentication
    :param auth_pass: resource pass authentication
    :param auth_type: resource type authentication
    :param user_agent: The string to identify ourselves with against the service
    :param throttle_connections: Wait X millisecond(s) between each request/connection
    :param group: The resourcegroup name - defaults to 'Default' if left empty
    :return: resource
    """
    resource = ResourceController.add_resource(server_name=server_name,
                                               server_address=server_address,
                                               server_id=server_id,
                                               resource_port=resource_port,
                                               resource_protocol=resource_protocol,
                                               auth_user=auth_user,
                                               auth_pass=auth_pass,
                                               auth_type=auth_type,
                                               user_agent=user_agent,
                                               recursive_sizes=recursive_sizes,
                                               basepath=basepath,
                                               display_url=display_url,
                                               description=description,
                                               throttle_connections=throttle_connections,
                                               group=group)
    return "resource added with id: %d" % resource.id

@app.route("/api/v2/resource/get", methods=["GET"])
@endpoint.api(
    parameter("by_owner", type=int, required=False, default=None),
    parameter("limit", type=int, default=10),
    parameter("offset", type=int, default=0),
    parameter("search", type=str, required=False, default=None)
)
def api_resource_get(by_owner, limit, offset, search):
    """
    Get resources.
    :param by_owner: Filter on resources by owner id
    :param limit:
    :param offset:
    :param search: hmmz
    :return:
    """
    args = {
        "limit": limit,
        "offset": offset
    }

    if by_owner:
        args["by_owner"] = by_owner

    # sanitize search query
    if search:
        if search.isdigit():
            args["port"] = int(search)
        elif search and len(search) <= 40:
            protocol = FileProtocols().id_by_name(search)
            if isinstance(protocol, int):
                args["protocol"] = protocol
            else:
                args["search"] = search

    resources = ResourceController.get_resources(**args)
    if isinstance(resources, Exception):
        return resources

    records = []
    records_total = 0
    if isinstance(args.get("limit"), int):
        _args = args
        _args.pop("limit")
        if isinstance(_args.get("offset"), int):
            _args.pop("offset")

        # @TODO we're only interested in the number of rows here,
        # so fetching the whole object is kinda overkill in terms
        # of performance. use count(*) sometime
        records_total = len(ResourceController.get_resources(**_args))

    for resource in resources:
        item = {
            "name": resource.server.name,
            "location": resource.resource_id,
            "protocol": resource.protocol_human,
            "files": resource.meta.file_count,
            "added": resource.date_added_ago,
            "updated": resource.date_crawl_end_ago,
            "options": None,
            "group": "Default"
        }
        records.append(item)

    return {
        "records": records,
        "queryRecordCount": records_total,
        "totalRecordCount": len(records)
    }

@app.route("/api/v2/resource/remove", methods=["POST"])
@endpoint.api(
    parameter("resource_id", type=int, required=True)
)
def api_resource_remove_post(resource_id):
    result = ResourceController.remove_resource(resource_id)
    return result

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

@app.route("/api/v2/resourcegroup/add", methods=["POST"])
@admin_required
@endpoint.api(
    parameter("name", type=str, required=True),
    parameter("description", type=str, required=False, default=None),
    parameter("crawl_interval", type=int, required=True, default=86400),
    parameter("amqp", type=str, required=False)
)
def api_resourcegroup_add(name, description, crawl_interval, amqp):
    """
    Add a resource group.
    :param name:
    :param description:
    :param crawl_interval:
    :param amqp:
    :return:
    """
    return ResourceGroupController.add(name=name, description=description,
                                       crawl_interval=crawl_interval, amqp=amqp)

@app.route("/api/v2/resourcegroup/get")
@admin_required
@endpoint.api(
    parameter("limit", type=int, default=10),
    parameter("offset", type=int, default=0),
    parameter("search", type=str, required=False, default=None)
)
def api_resourcegroup_get(limit, offset, search):
    """
    Get resource groups.
    :param by_owner: Filter on resources by owner id
    :param limit:
    :param offset:
    :param search: hmmz
    :return:
    """
    args = {
        "limit": limit,
        "offset": offset
    }

    records = []
    groups = ResourceGroupController.get(limit=limit, offset=offset, search=search)

    for group in groups:
        group_json = group.get_json()
        group_json['date_added'] = group.date_added_human
        records.append(group_json)

    # bleh
    args.pop('limit')
    args.pop('offset')

    records_total = db.session.query(func.count(ResourceGroup.id)).scalar()

    return {
        "records": groups,
        "queryRecordCount": records_total,
        "totalRecordCount": len(groups)
    }

@app.route("/api/v2/resourcegroup/assign_amqp")
@admin_required
@endpoint.api(
    parameter("resourcegroup_id", type=int, required=True),
    parameter("amqp_id", type=int, required=True)
)
def api_admin_resourcegroup_assign_amqp(resourcegroup_id, amqp_id):
    ResourceGroupController.assign_amqp(resourcegroup_id, amqp_id)
    return True