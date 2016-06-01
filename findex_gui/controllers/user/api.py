import flask
from flask import session

from flask_restful import reqparse, abort
from flask.ext.restful import Resource

from findex_gui import appapi
from findex_gui.controllers.user.user import UserController


class UserRegister(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        self.reqparse.add_argument('username', location='json', type=str, required=True, help='key is required')
        self.reqparse.add_argument('password', location='json', type=str, required=True, help='key is required')

        super(UserRegister, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        args = {k: v for k, v in args.items() if v is not None}

        user = UserController().register(username=args['username'],
                                         password=args['password'])

        if isinstance(user, Exception):
            return abort(404, message=str(user))
        else:
            return flask.jsonify(**args)


#appapi.add_resource(UserRegister, '/api/v2/user/register', endpoint='user_register')