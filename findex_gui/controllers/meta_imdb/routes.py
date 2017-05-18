from findex_gui.web import app, themes
from findex_gui.controllers.meta_imdb.controller import MetaImdbController
import findex_gui.controllers.meta_imdb.converters


@app.route("/meta/popcorn")
def meta_popcorn():
    results = MetaImdbController.search()
    return themes.render("main/meta/popcorn", results=results)


@app.route("/meta/popcorn/<popcorn:parsed>")
def meta_popcorn_search(parsed):
    results = MetaImdbController.search(**parsed)
    return themes.render("main/meta/popcorn", results=results, filters=parsed)


@app.route("/meta/popcorn/cast/<path:path>")
def meta_popcorn_actor(path):
    results = MetaImdbController.get_actor_played_in(path)
    return themes.render("main/meta/person", results=results, person=path, title="actor")


@app.route("/meta/popcorn/director/<path:path>")
def meta_popcorn_director(path):
    results = MetaImdbController.get_director_directed(path)
    return themes.render("main/meta/person", results=results, person=path, title="director")
