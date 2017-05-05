from findex_gui import app, themes
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
