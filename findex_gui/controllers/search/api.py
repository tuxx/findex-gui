import flask

from findex_gui import app, appapi
from findex_gui.controllers.search.search import SearchController
from findex_gui.controllers.helpers import findex_api, ApiArgument as api_arg

from findex_common.static_variables import FileCategories


@app.route("/api/v2/search/<string:key>", methods=["GET"])
def api_search_get(key):
    controller = SearchController()
    result = controller.search(key=key)
    return flask.jsonify(**result.get_json())


@app.route("/api/v2/search/<string:key>", methods=["POST"])
@findex_api(
    api_arg("file_categories", type=list,
            help="A list of options: %s" % ", ".join(FileCategories().get_names())),
    api_arg("file_extensions", type=list,
            help="A list of file extensions, without the dot."),
    api_arg("file_type", type=list,
            help="A list of options: \"files\", \"dirs\", \"both\""),
    api_arg("file_size", type=str,
            help="A range of bytes represented in a list of 2 elements"),
    api_arg("page", type=int,
            help="An integer that determines the paging"),
    api_arg("per_page", type=int,
            help="An integer that determines the amount of results"),
    api_arg("lazy_search", type=bool,
            help="Set to true for better search performance but less accuracy. Most suited "
                 "for auto completion on the front-end."),
    api_arg("autocomplete", type=bool,
            help="this is the same as setting `lazy_search` to true and `per_page` to 5"),
)
def api_search_post(key, data):
    controller = SearchController()
    result = controller.search(key, **data)
    return result.get_json()
