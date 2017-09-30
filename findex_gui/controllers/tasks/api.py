from flask_yoloapi import endpoint, parameter

from findex_gui.web import app
from findex_gui.controllers.tasks.tasks import TaskController


@app.route("/api/v2/task/add", methods=["POST"])
@endpoint.api(
    parameter("name", type=str, required=True),
    parameter("owner_id", type=int, required=False),
    parameter("options", type=dict, required=False)
)
def api_task_add(name, owner_id, options):
    """
    Adds a task.
    :param name: task name
    :param owner_id: owner id
    :param options: options like 'interval' and 'retry'
    :return:
    """
    task = TaskController.add_task(name, owner_id, options)
    return "task added with id: %d" % task.id


@app.route("/api/v2/task/get", methods=["POST"])
@endpoint.api(
    parameter("by_owner", type=int, required=False, default=None)
)
def api_task_get(by_owner):
    """
    Fetches a task.
    :param by_owner: filtered by owner id
    :return:
    """
    data = TaskController.get_tasks(by_owner)
    return data


@app.route("/api/v2/task/assign_resource_group", methods=["POST"])
@endpoint.api(
    parameter("task_id", type=int, required=True),
    parameter("resourcegroup_id", type=int, required=True)
)
def api_task_assign_resource_group(task_id, resourcegroup_id):
    """
    Assigns a task to a resource group
    :param task_id: task id
    :param resourcegroup_id: resource group id
    :return:
    """
    data = TaskController.assign_resource_group(task_id, resourcegroup_id)
    return data


@app.route("/api/v2/task/add", methods=["POST"])
@endpoint.api(
    parameter("task_id", type=int, required=True),
    parameter("resourcegroup_id", type=int, required=True)
)
def api_task_remove_resource_group(task_id, resourcegroup_id):
    """
    Removes a task from a resource group
    :param task_id: task id
    :param resourcegroup_id: resource group id
    :return:
    """
    data = TaskController.remove_resource_group()
    return data
