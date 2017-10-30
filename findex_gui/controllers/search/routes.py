import flask
from flask import session, redirect, url_for
import findex_gui.controllers.search.converters
from findex_gui.web import app, themes
from findex_gui.controllers.search.search import SearchController


@app.route('/search')
def search_home():
    return redirect("%ssearch/*&type=[files]" % app.config["APPLICATION_ROOT"], 302)


@app.route('/search/<search:parsed>')
def search(parsed):
    search = SearchController()

    errors = []
    results = []

    try:
        # @TO-DO: check theme whether to do REST API searching or flask->jinja2
        #results = search.search(**args)
        pass
    except Exception as ex:
        errors.append('error %s' % str(ex))

    return themes.render('main/search', results=[], errors=errors, session=session)