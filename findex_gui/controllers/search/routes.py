import flask
from flask import session
import findex_gui.controllers.search.converters
from findex_gui import app, themes
from findex_gui.controllers.search.search import SearchController


@app.route('/search')
def search_home():
    return themes.render('main/search')


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