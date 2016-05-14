from findex_gui import app

@app.errorhandler(500)
def application_error(e):
    return str(e)

@app.errorhandler(404)
def page_not_found(e):
    #return render_template('404.html'), 404
    e = ''
    return '404'