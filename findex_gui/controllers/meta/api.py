from flask_yoloapi import endpoint, parameter
from findex_gui.web import app, db
from findex_gui.orm.models import MetaMovies
from findex_gui.controllers.meta.controller import MetaPopcornController


@app.route("/api/v2/meta/popcorn/actor/search/<string:key>", methods=["GET"])
@endpoint.api()
def api_meta_popcorn_cast_search(key):
    results = MetaPopcornController.get_actors(search=key)
    return {
        "items": [{"actor": z, "id": z} for z in results],
        "total_count": len(results),
        "incomplete_results": False
    }


@app.route("/api/v2/meta/popcorn/director/search/<string:key>", methods=["GET"])
@endpoint.api()
def api_meta_popcorn_director_search(key):
    results = MetaPopcornController.get_director(search=key)
    return {
        "items": [{"director": z, "id": z} for z in results],
        "total_count": len(results),
        "incomplete_results": False
    }


@app.route("/api/v2/meta/popcorn/details/<int:meta_movie_id>", methods=["GET"])
@endpoint.api()
def api_meta_popcorn_get_details(meta_movie_id):
    meta_movie = db.session.query(MetaMovies).filter(MetaMovies.id == meta_movie_id).first()
    if not meta_movie:
        raise Exception("meta_movie_id by that id not found")
    local_files = MetaPopcornController.get_details(meta_movie_id)
    return {
        "local_files": local_files,
        "meta_movie": meta_movie
    }
