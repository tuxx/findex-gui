import flask
from flask import session

from flask_restful import reqparse, abort
from flask.ext.restful import Resource

from findex_gui import appapi

keys = [
    'search_display_view'
]


class SessionGet(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        self.reqparse.add_argument('key', location='json', type=str, required=True, help='key is required')

        super(SessionGet, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        args = {k: v for k, v in args.items() if v is not None}

        if not args['key'] in keys:
            return abort(404, message="key \"%s\" doesn't exist" % args['key'])

        if not args['key'] in session:
            session[args['key']] = 'fancy'

        return flask.jsonify(**{
            'value': session[args['key']]
        })


class SessionSet(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        self.reqparse.add_argument('key', location='json', type=str, required=True, help='key is required')
        self.reqparse.add_argument('val', location='json', type=str, required=True, help='value is required')

        super(SessionSet, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        args = {k: v for k, v in args.items() if v is not None}

        if not args['key'] in keys:
            return abort(404, message="key \"%s\" doesn't exist" % args['key'])

        if not args['val'] in ['table', 'fancy']:
            return abort(404, message="could not set val \"%s\" - doesn't exist" % args['val'])

        session[args['key']] = args['val']
        print session[args['key']]

        return flask.jsonify(**{
            'message': 'ok'
        })

appapi.add_resource(SessionSet, '/api/v2/session/set', endpoint='api_session_set')
appapi.add_resource(SessionGet, '/api/v2/session/get', endpoint='api_session_get')

