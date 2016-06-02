from flask import request, session
from flaskext.auth.auth import get_current_user_data

from findex_gui import app
from findex_gui import babel, locales


@app.before_request
def require_authorization():
    if 'db_file_count' in app.config:
        if not request.path in ['/'] and not request.path.startswith('/browse'):
            return

    from findex_gui import db

    app.config['db_file_count'] = int(db.session.execute("""
    SELECT reltuples::int FROM pg_class WHERE relname ='files'
    """).first()[0])


@babel.localeselector
def get_locale():
    """
    Try to determine the locale based on the:
    - currently logged in user preference
    or
    - session cookie preference
    or
    - 'Accept-Language' user agent
    """

    user = get_current_user_data()
    if user:
        return user['locale']
    elif 'locale' in session:
        return session['locale']
    else:
        return request.accept_languages.best_match(locales.keys())