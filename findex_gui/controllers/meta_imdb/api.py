from flask_yoloapi import endpoint, parameter
from findex_gui.web import app
from findex_gui.controllers.meta_imdb.controller import MetaImdbController


@app.route("/api/v2/meta/imdb/actor/search/<string:key>", methods=["GET"])
@endpoint.api()
def api_meta_imdb_cast_search(key):
    results = MetaImdbController.get_actors(search=key)
    return {
        "items": [{"actor": z.actor, "id": z.id} for z in results],
        "total_count": len(results),
        "incomplete_results": False
    }


@app.route("/api/v2/meta/imdb/director/search/<string:key>", methods=["GET"])
def api_meta_imdb_director_search(key):
    results = MetaImdbController.get_director(search=key)
    return {
        "items": [{"director": z.director, "id": z.id} for z in results],
        "total_count": len(results),
        "incomplete_results": False
    }
