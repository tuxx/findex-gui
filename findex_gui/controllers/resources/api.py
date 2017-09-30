from flask import jsonify
from flask_yoloapi import endpoint, parameter

from findex_gui.web import app
from findex_gui.bin import validators
from findex_gui.controllers.resources.resources import ResourceController
from findex_common.static_variables import FileProtocols


@app.route("/api/v2/resource/add", methods=["POST"])
@endpoint.api(
    parameter("server_name", type=str, required=False),
    parameter("server_address", type=str, required=False),
    parameter("server_id", type=int, required=False),

    parameter("resource_port", type=int, required=True),
    parameter("resource_protocol", type=int, required=True, validator=validators.server_protocol),

    parameter("auth_user", type=str, required=False),
    parameter("auth_pass", type=str, required=False),
    parameter("auth_type", type=str, required=False),

    parameter("user_agent", type=str, required=False),
    parameter("recursive_sizes", type=bool, required=False),

    parameter("basepath", type=str, required=True),
    parameter("display_url", type=str, required=False),
    parameter("description", type=str, required=False)
)
def api_resource_add_post(server_name, server_address, server_id,
                          resource_port, resource_protocol,
                          auth_user, auth_pass, auth_type,
                          user_agent, recursive_sizes, basepath,
                          display_url, description):
    """
    Adds a local or remote file resource
    :param server_name: Server name
    :param server_address: ipv4 'str' - clean hostname or IP
    :param server_id: server DB id
    :param resource_port: valid port number
    :param resource_protocol: valid protocol number 'int' - see `findex_common.static_variables.FileProtocols`
    :param description: resource description 'str'
    :param display_url: url prefix as it will be shown on the front-end 'str'
    :param basepath: the absolute crawl root path 'str'
    :param recursive_sizes: recursively calculate directory sizes (performance impact during crawl)
    :param auth_user: resource user authentication 'str'
    :param auth_pass: resource pass authentication 'str'
    :param auth_type: resource type authentication 'str'
    :param user_agent: The string to identify ourselves with against the service 'str'
    :param throttle_connections: Wait X seconds between each request/connection 'int'
    :return: resource
    """
    resource = ResourceController.add_resource(
        server_name=server_name, server_address=server_address, server_id=server_id,
        resource_port=resource_port, resource_protocol=resource_protocol,
        auth_user=auth_user, auth_pass=auth_pass, auth_type=auth_type,
        user_agent=user_agent, recursive_sizes=recursive_sizes,
        basepath=basepath, display_url=display_url, description=description)
    return "resource added with id: %d" % resource.id


@app.route("/api/v2/resource/get", methods=["GET"])
@endpoint.api(
    parameter("by_owner", type=int, required=False, default=None),
    parameter("perPage", type=int, required=False, default=None),
    parameter("page", type=int, required=False, default=None),
    # parameter("queries[search]", type=str, required=False)
    parameter("search", type=str, required=False, default=None)
)
def api_resource_get(by_owner, perPage, page, search):
    """
    Get resources.
    :param by_owner: Filter on resources by owner id
    :param perPage:
    :param page:
    :param queries: hmmz
    :return:
    """
    args = {}
    if perPage:
        args["limit"] = perPage
        if page:
            args["offset"] = (page - 1) * perPage
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

    return jsonify({
        "records": records,
        "queryRecordCount": records_total,
        "totalRecordCount": len(records)
    })


@app.route("/api/v2/resource/remove", methods=["POST"])
@endpoint.api(
    parameter("resource_id", type=int, required=True)
)
def api_resource_remove_post(resource_id):
    result = ResourceController.remove_resource(resource_id)
    return result
