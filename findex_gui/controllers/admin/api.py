import flask

from flask_restful import reqparse, abort
from flask.ext.restful import Resource

from findex_gui import appapi
from findex_gui.controllers.user.decorators import admin_required
from findex_gui.controllers.options.options import OptionsController


class OptionsGetAPI(Resource):
    decorators = [admin_required]
    keys = [
        'theme_active'
    ]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        self.reqparse.add_argument('key', location='json', type=str, required=True, help='key is required')

        super(OptionsGetAPI, self).__init__()

    def get(self, key):
        global keys

        controller = OptionsController.get(key)

        if controller:
            return flask.jsonify(**{key: controller.val})
        else:
            return abort(404, message='Unknown key \'%s\'' % key)


class OptionsPostAPI(Resource):
    decorators = [admin_required]
    keys = [
        'theme_active',
    ]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        self.reqparse.add_argument('key', location='json', type=str, required=True, help='key is required')
        self.reqparse.add_argument('val', location='json', type=str, required=True, help='key is required')

        super(OptionsPostAPI, self).__init__()

    def post(self):
        global keys

        args = self.reqparse.parse_args()
        args = {k: v for k, v in args.items() if v is not None}

        if not args['key'] in keys:
            return abort(404, message='Unknown key \'%s\'' % args['key'])

        OptionsController.set(key=args['key'],
                              val=args['val'])

        return flask.jsonify(**{'message': 'key set'})


appapi.add_resource(OptionsPostAPI, '/api/v2/admin/option_set', endpoint='api_admin_option_set')
appapi.add_resource(OptionsGetAPI, '/api/v2/admin/option_get', endpoint='api_admin_option_get')