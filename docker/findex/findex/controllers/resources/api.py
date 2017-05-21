import flask

from findex_gui.web import app
from findex_gui.controllers.helpers import findex_api, ApiArgument as api_arg
from findex_gui.controllers.resources.resources import ResourceController


@app.route("/api/v2/resource/add", methods=["POST"])
@findex_api(
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
    api_arg("throttle_connections", location="json", type=bool, required=False,
            help="wait X seconds between each request/connection"),
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
        return flask.jsonify(**{"success": True})


@app.route("/api/v2/resource/get", methods=["POST"])
@findex_api(
    api_arg("by_owner", location="json", type=int, required=False,
            help="Filter on resources that owner id owns")
)
def api_resource_get_post(data):
    resources = ResourceController.get_resources(**data)
    if isinstance(resources, Exception):
        return resources
    else:
        a = resources[0].get_json()
        return resources


@app.route("/api/v2/resource/remove", methods=["POST"])
@findex_api(
    api_arg("resource_id", location="json", type=int, required=False,
            help="The resource ID")
)
def api_resource_remove_post(data):
    result = ResourceController.remove_resource(**data)
    if isinstance(result, Exception):
        return result
    else:
        return flask.jsonify(**{"success": True, "data": result})
