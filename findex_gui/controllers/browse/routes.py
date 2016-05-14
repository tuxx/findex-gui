import flask

from findex_gui import app, themes
import findex_gui.controllers.browse.converters
from findex_gui.controllers.browse.browse import Browse


@app.route('/browse')
def browse_home():
    e = ''
    return themes.render('main/browse')


@app.route('/browse/<browse:parsed>')
def browse(parsed):
    if not parsed:
        return 'w0w debug diz'

    browse = Browse()

    if parsed['path'].endswith('/'):
        data = browse.browse(parsed)

        return themes.render('main/browse_dir', **data)
    else:
        browse.inspect(parsed)

        return themes.render('main/browse_dir', **data)