import flask

from findex_gui import app, appapi
from findex_gui.controllers.search.search import SearchController
from flask_restful import reqparse, abort, Api, Resource
from findex_common.static_variables import FileCategories


class SearchAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        self.reqparse.add_argument('file_categories', location='json', type=list,
                                   help='A list of options: %s' % ', '.join(FileCategories().get_names()))

        self.reqparse.add_argument('file_extensions', location='json', type=list,
                                   help='A list of file extensions, without the dot.')

        self.reqparse.add_argument('file_type', type=list, location='json',
                                   help='A list of options: \'files\', \'dirs\', \'both\'')

        self.reqparse.add_argument('file_size', type=str, location='json',
                                   help='A range of bytes represented in a list of 2 elements')

        self.reqparse.add_argument('page', type=int, location='json',
                                   help='An integer that determines the paging')

        self.reqparse.add_argument('per_page', type=int, location='json',
                                   help='An integer that determines the amount of results')

        self.reqparse.add_argument('lazy_search', type=bool, location='json',
                                   help='Set to true for better search performance but less accuracy. Most suited ' +
                                   'for auto completion on the front-end.')

        self.reqparse.add_argument('autocomplete', type=bool, location='json',
                                   help='this is the same as setting `lazy_search` to true and `per_page` to 5')

        super(SearchAPI, self).__init__()

    def get(self, key):
        controller = SearchController()
        result = controller.search(key=key)

        return flask.jsonify(**result.to_json())

    def post(self, key):
        # ---- make decorator of this with try catch oin parse_args (it can fail)
        args = self.reqparse.parse_args()
        args = {k: v for k, v in list(args.items()) if v is not None}
        # ----

        try:
            controller = SearchController()
            result = controller.search(key, **args)
        except Exception as ex:
            return abort(404, message=str(ex))

        return flask.jsonify(**result.to_json())

appapi.add_resource(SearchAPI, '/api/v2/search/<string:key>', endpoint='api_search')