from findex_gui import app
from flask import request
#SELECT reltuples::int FROM pg_class WHERE relname ='files'


@app.before_request
def require_authorization():
    if 'db_file_count' in app.config:
        if not request.path in ['/'] and not request.path.startswith('/browse'):
            return

    from findex_gui import db

    app.config['db_file_count'] = int(db.session.execute("""
    SELECT reltuples::int FROM pg_class WHERE relname ='files'
    """).first()[0])
