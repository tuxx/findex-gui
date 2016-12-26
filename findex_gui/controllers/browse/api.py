import flask

from findex_gui.controllers.user.user import UserController
from findex_gui.orm.queries import Findex
from findex_gui import app, locales


@app.route('/api/v2/browse/servers', methods=['GET'])
def api_browse_servers():
    if UserController.is_admin():
        resources = [resource.to_json() for resource in Findex().get_resources()]
        return flask.jsonify(**{"status": True, "data": resources})
    else:
        # do something with roles here
        return flask.jsonify(**{"a": 1})