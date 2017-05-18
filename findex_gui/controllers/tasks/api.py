import flask
from flask_restful import reqparse, abort
from flask_restful import Resource

from findex_gui.web import app, locales, appapi
from findex_gui.controllers.tasks.tasks import TaskController


class TaskAdd(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', location='json', type=str, required=True,
                                   help='Server name')
        self.reqparse.add_argument('owner_id', location='json', type=int, required=False,
                                   help='Server IPV4 string')
        self.reqparse.add_argument('options', location='json', type=dict, required=False,
                                   help='task options')
        super(TaskAdd, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        args = {k: v for k, v in list(args.items()) if v is not None}

        resource = TaskController.add_task(**args)
        if isinstance(resource, Exception):
            return abort(404, message=str(resource))
        else:
            return flask.jsonify(**{'success': True})


class TaskGet(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('by_owner', location='json', type=int, required=False,
                                   help='Filter on resources that owner id owns')
        super(TaskGet, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        args = {k: v for k, v in list(args.items()) if v is not None}

        data = TaskController.get_tasks(**args)
        if isinstance(data, Exception):
            return abort(404, message=str(data))
        else:
            return flask.jsonify(**{'success': True, 'data': data})


class TaskAssignResourceGroup(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('task_id', location='json', type=int, required=True,
                                   help='the task id')
        self.reqparse.add_argument('resourcegroup_id', location='json', type=int, required=True,
                                   help='the task id')
        super(TaskAssignResourceGroup, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        args = {k: v for k, v in list(args.items()) if v is not None}

        data = TaskController.assign_resource_group(**args)
        if isinstance(data, Exception):
            return abort(404, message=str(data))
        else:
            return flask.jsonify(**{'success': True, 'data': data})


class TaskRemoveResourceGroup(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('task_id', location='json', type=int, required=True,
                                   help='the task id')
        self.reqparse.add_argument('resourcegroup_id', location='json', type=int, required=True,
                                   help='the task id')
        super(TaskRemoveResourceGroup, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        args = {k: v for k, v in list(args.items()) if v is not None}

        data = TaskController.remove_resource_group(**args)
        if isinstance(data, Exception):
            return abort(404, message=str(data))
        else:
            return flask.jsonify(**{'success': True, 'data': data})

appapi.add_resource(TaskAdd, '/api/v2/task/add', endpoint='api_task_add')
appapi.add_resource(TaskGet, '/api/v2/task/get', endpoint='api_task_get')
appapi.add_resource(TaskAssignResourceGroup, '/api/v2/task/assign_resource_group', endpoint='api_task_assign_resource_group')
appapi.add_resource(TaskRemoveResourceGroup, '/api/v2/task/remove_resource_group', endpoint='api_task_remove_resource_group')
