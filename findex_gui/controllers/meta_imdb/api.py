import flask

from flask_restful import reqparse, abort, Resource

from findex_gui.web import appapi
from findex_gui.controllers.meta_imdb.controller import MetaImdbController


class MetaImdbSearchActor(Resource):
    def get(self, key):
        try:
            results = MetaImdbController.get_actors(search=key)
            return flask.jsonify({
                "items": [{"actor": z.actor, "id": z.id} for z in results],
                "total_count": len(results),
                "incomplete_results": False
            })
        except Exception as ex:
            return abort(404, message=str(ex))


class MetaImdbSearchDirector(Resource):
    def get(self, key):
        try:
            results = MetaImdbController.get_director(search=key)
            return flask.jsonify({
                "items": [{"director": z.director, "id": z.id} for z in results],
                "total_count": len(results),
                "incomplete_results": False
            })
        except Exception as ex:
            return abort(404, message=str(ex))


appapi.add_resource(MetaImdbSearchActor, "/api/v2/meta/imdb/actor/search/<string:key>",
                    endpoint="api_meta_imdb_cast_search")
appapi.add_resource(MetaImdbSearchDirector, "/api/v2/meta/imdb/director/search/<string:key>",
                    endpoint="api_meta_imdb_director_search")
