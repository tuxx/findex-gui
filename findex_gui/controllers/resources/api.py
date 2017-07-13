import flask

from findex_common.static_variables import FileProtocols
from findex_gui.web import app
from findex_gui.bin.api import FindexApi, api_arg
from findex_gui.controllers.resources.resources import ResourceController


@app.route("/api/v2/resource/add", methods=["POST"])
@FindexApi(
    api_arg("server_name", location="json", type=str, required=False,
            help="Server name"),
    api_arg("server_address", location="json", type=str, required=False,
            help="Server IPV4 string"),
    api_arg("server_id", location="json", type=int, required=False,
            help="Server ID"),

    api_arg("resource_port", location="json", type=int, required=True,
            help="Server port"),
    api_arg("resource_protocol", location="json", type=int, required=True,
            help="Valid protocol number 0:ftp 1:filesystem 2:smb 3:sftp 4:http 5:https"),

    api_arg("auth_user", location="json", type=str, required=False,
            help="Username authentication"),
    api_arg("auth_pass", location="json", type=str, required=False,
            help="Password authentication"),
    api_arg("auth_type", location="json", type=str, required=False,
            help="Authentication type"),

    api_arg("user_agent", location="json", type=str, required=False,
            help="The string to identify ourselves with against the service."),
    api_arg("recursive_sizes", location="json", type=bool, required=False,
            help="Recursively calculate directory sizes (performance impact during crawl),"),
    # api_arg("throttle_connections", location="json", type=bool, required=False,
    #         help="wait X seconds between each request/connection"),
    api_arg("basepath", location="json", type=str, required=True,
            help="The absolute crawl root path"),
    api_arg("display_url", location="json", type=str, required=False,
            help="Url prefix to use in URL generation"),
    api_arg("description", location="json", type=str, required=False,
            help="Resource description"),
)
def api_resource_add_post(data):
    resource = ResourceController.add_resource(**data)
    if isinstance(resource, Exception):
        return resource
    else:
        return True


@app.route("/api/v2/resource/get", methods=["GET"])
@FindexApi(
    api_arg("by_owner", location="json", type=int, required=False, help="Filter on resources that owner id owns"),
    api_arg("perPage", location="json", type=int, required=False, help="limit"),
    api_arg("page", location="json", type=int, required=False, help="limit"),
    api_arg("queries[search]", location="json", type=str, required=False,
            help="Search by: IP, Name, Protocol")
)
def api_resource_get(data):
    args = {}
    if data.get("perPage"):
        args["limit"] = data.get("perPage")
        if data.get("page"):
            args["offset"] = (data.get("page") - 1) * data.get("perPage")
    if data.get("by_owner"):
        args["by_owner"] = data.get("by_owner")

    # sanitize search query
    if data.get("queries[search]"):
        search = data.get("queries[search]")
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
            "date_added": resource.date_added_ago,
            "last_crawl": resource.date_crawl_end_ago,
            "options": "ehh",
            "group": "Default"
        }
        records.append(item)

    return flask.jsonify({
        "records": records,
        "queryRecordCount": records_total,
        "totalRecordCount": len(records)
    })


@app.route("/api/v2/resource/remove", methods=["POST"])
@FindexApi(
    api_arg("resource_id", location="json", type=int, required=False,
            help="The resource ID")
)
def api_resource_remove_post(data):
    result = ResourceController.remove_resource(**data)
    if isinstance(result, Exception):
        return result
    else:
        return flask.jsonify(**{"success": True, "data": result})
