import os
from findex_gui.web import app
from flask import render_template, request, flash, session, redirect, url_for, send_from_directory, abort


@app.route('/static/<path:filename>')
def static(filename):
    if filename.startswith('/'):
        return abort(404)

    from findex_gui.web import themes

    filename = filename.replace('..', '')
    filename = filename.replace('./', '')

    search_dirs = ['static/']

    if filename.startswith('themes/'):
        spl = filename.split('/')

        if len(spl) >= 3 and spl[2] == 'static':
            filename = '/'.join(spl[3:])
            search_dirs.insert(0, 'themes/%s/static/' % spl[1])

    for search_dir in search_dirs:
        directory = '%s/%s' % (app.config['dir_base'], search_dir)

        if os.path.isfile(directory + filename):
            return send_from_directory(directory, filename)

    return themes.render('errors/404', status_code=404)