import flask
from flask import request

from flaskext.auth import get_current_user_data
from flask_restful import reqparse, abort
from flask_restful import Resource

from findex_gui import app, locales, appapi
from findex_gui.orm.models import User
from findex_gui.controllers.user.decorators import login_required
from findex_gui.controllers.user.user import UserController


@app.route('/api/v2/user/locale', methods=['POST'])
def api_user_locale():
    e = ''


@app.route('/api/v2/user/locale/all', methods=['GET'])
def api_user_locale_available():
    return flask.jsonify(**locales)


@app.route('/api/v2/user/locale/set', methods=['POST'])
def api_user_locale_set():
    if 'lang' not in request.form:
        return flask.jsonify(**{'fail': 'parameter \'lang\' not given'}), 400

    try:
        if request.authorization or get_current_user_data():
            if request.authorization:
                user = UserController.authenticate_basic()
            else:
                user = User.query.filter(
                    User.id == get_current_user_data()['id']).one()
            if user:
                UserController.locale_set(
                    locale=request.form['lang'], user=user)
                return flask.jsonify(**{'success': True}), 201

        UserController.locale_set(locale=request.form['lang'])
        return flask.jsonify(**{'success': True}), 201
    except Exception as ex:
        return flask.jsonify(**{'fail': str(ex)}), 400


class UserRegister(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', location='json', type=str, required=True, help='Username')
        self.reqparse.add_argument('password', location='json', type=str, required=True, help='Password')
        super(UserRegister, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        args = {k: v for k, v in args.items() if v is not None}

        user = UserController.user_add(username=args['username'], password=args['password'])
        if isinstance(user, Exception):
            return abort(404, message=str(user))
        else:
            return flask.jsonify(**{'success': True})


class UserDelete(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', location='json', type=str, required=True, help='Username')
        super(UserDelete, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        args = {k: v for k, v in args.items() if v is not None}

        user = UserController.user_delete(username=args['username'])
        if isinstance(user, Exception):
            return abort(404, message=str(user))
        else:
            return flask.jsonify(**args)

appapi.add_resource(UserRegister, '/api/v2/user/delete', endpoint='api_user_delete')
appapi.add_resource(UserRegister, '/api/v2/user/register', endpoint='api_user_register')
