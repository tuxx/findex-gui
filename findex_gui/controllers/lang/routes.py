from flask import request

from findex_gui import babel, languages


@babel.localeselector
def get_locale():
    return 'nl'
    #return request.accept_languages.best_match(languages.keys())