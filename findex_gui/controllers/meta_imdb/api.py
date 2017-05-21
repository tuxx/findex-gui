import flask
from flask import abort

from findex_gui.web import app
from findex_gui.controllers.helpers import findex_api, ApiArgument as api_arg
from findex_gui.controllers.meta_imdb.controller import MetaImdbController


@app.route("/api/v2/meta/imdb/actor/search/<string:key>", methods=["GET"])
def api_meta_imdb_cast_search(key):
    try:
        results = MetaImdbController.get_actors(search=key)
        return flask.jsonify({
            "items": [{"actor": z.actor, "id": z.id} for z in results],
            "total_count": len(results),
            "incomplete_results": False
        })
    except Exception as ex:
        return abort(404, message=str(ex))


@app.route("/api/v2/meta/imdb/director/search/<string:key>", methods=["GET"])
def api_meta_imdb_director_search(key):
    try:
        results = MetaImdbController.get_director(search=key)
        return flask.jsonify({
            "items": [{"director": z.director, "id": z.id} for z in results],
            "total_count": len(results),
            "incomplete_results": False
        })
    except Exception as ex:
        return abort(404, message=str(ex))
