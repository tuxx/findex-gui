from findex_gui import app, themes


@app.route('/')
def root():
    return themes.render('main/home')


@app.errorhandler(404)
def error(e):
    return themes.render('main/error', msg=str(e))
