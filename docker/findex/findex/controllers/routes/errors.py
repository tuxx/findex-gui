from flask import Response

from findex_gui.bin.config import config
from findex_gui.web import app


@app.errorhandler(404)
def page_not_found(e):
    print(e)
    return '404', 404


@app.errorhandler(Exception)
def all_exception_handler(error):
    rtn = 'Error'

    if config("findex:findex:debug"):
        if hasattr(error, "message"):
            rtn += ': %s' % error.message
        else:
            rtn += ': %s' % str(error)
    else:
        rtn += "Error"

    rtn = Response(rtn, content_type="text/plain")

    return rtn, 500