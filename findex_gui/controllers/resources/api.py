import flask
from flask import request

from flaskext.auth import get_current_user_data
from flask_restful import reqparse, abort
from flask_restful import Resource

from findex_gui import app, locales, appapi
from findex_gui.orm.models import User
from findex_gui.controllers.user.decorators import login_required
from findex_gui.controllers.resources.resources import ResourceController


class ResourceAdd(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('server_name', location='json', type=str, required=False,
                                   help='Server name')
        self.reqparse.add_argument('server_address', location='json', type=str, required=False,
                                   help='Server IPV4 string')
        self.reqparse.add_argument('server_id', location='json', type=int, required=False,
                                   help='Server ID')

        self.reqparse.add_argument('resource_port', location='json', type=int, required=True,
                                   help='Server port')
        self.reqparse.add_argument('resource_protocol', location='json', type=int, required=True,
                                   help='Valid protocol number 0:ftp 1:filesystem 2:smb 3:sftp 4:http 5:https')

        self.reqparse.add_argument('auth_user', location='json', type=str, required=False,
                                   help='Username authentication')
        self.reqparse.add_argument('auth_pass', location='json', type=str, required=False,
                                   help='Password authentication')
        self.reqparse.add_argument('auth_type', location='json', type=str, required=False,
                                   help='Authentication type')

        self.reqparse.add_argument('recursive_sizes', location='json', type=bool, required=False,
                                   help='Recursively calculate directory sizes (performance impact during crawl)')
        self.reqparse.add_argument('basepath', location='json', type=str, required=True,
                                   help='The absolute crawl root path')
        self.reqparse.add_argument('display_url', location='json', type=str, required=False,
                                   help='Url prefix to use in URL generation')
        self.reqparse.add_argument('description', location='json', type=str, required=False,
                                   help='Resource description')
        super(ResourceAdd, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        args = {k: v for k, v in args.items() if v is not None}

        resource = ResourceController.add_resource(**args)
        if isinstance(resource, Exception):
            return abort(404, message=str(resource))
        else:
            return flask.jsonify(**{'success': True})


appapi.add_resource(ResourceAdd, '/api/v2/resource/add', endpoint='api_resource_add')
