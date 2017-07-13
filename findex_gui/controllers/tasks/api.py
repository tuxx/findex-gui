import flask
from findex_gui.web import app

from findex_gui.bin.api import FindexApi, api_arg
from findex_gui.controllers.tasks.tasks import TaskController


@app.route("/api/v2/task/add", methods=["POST"])
@FindexApi(
    api_arg("name", type=str, required=True, help="Server name"),
    api_arg("owner_id", type=int, required=False, help="Server IPV4 string"),
    api_arg("options", type=dict, required=False, help="task options")
)
def api_task_add(data):
    resource = TaskController.add_task(data)
    if isinstance(resource, Exception):
        return resource
    return True


@app.route("/api/v2/task/get", methods=["POST"])
@FindexApi(
    api_arg("by_owner", type=int, required=False, help="Filter on resources that owner id owns")
)
def api_task_get(data):
    data = TaskController.get_tasks(data)
    return data


@app.route("/api/v2/task/assign_resource_group", methods=["POST"])
@FindexApi(
    api_arg("task_id", type=int, required=True, help="the task id"),
    api_arg("resourcegroup_id", type=int, required=True, help="the task id")
)
def api_task_assign_resource_group(data):
    data = TaskController.assign_resource_group(data)
    return data


@app.route("/api/v2/task/add", methods=["POST"])
@FindexApi(
    api_arg("task_id", type=int, required=True, help="the task id"),
    api_arg("resourcegroup_id", type=int, required=True, help="the task id")
)
def api_task_remove_resource_group(data):
    data = TaskController.remove_resource_group(data)
    return data
