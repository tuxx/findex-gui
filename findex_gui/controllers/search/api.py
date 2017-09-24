import flask

from findex_gui.web import app
from findex_gui.controllers.search.search import SearchController
from flask_yoloapi import endpoint, parameter

from findex_common.static_variables import FileCategories


@app.route("/api/v2/search/<string:key>", methods=["GET"])
def api_search_get(key):
    controller = SearchController()
    result = controller.search(key=key)
    return flask.jsonify(**result.get_json())


@app.route("/api/v2/search/<string:key>", methods=["POST"])
@endpoint.api(
    parameter("file_categories", type=list),
    parameter("file_extensions", type=list),
    parameter("file_type", type=list),
    parameter("file_size", type=str),
    parameter("page", type=int, default=0),
    parameter("per_page", type=int),
    parameter("lazy_search", type=bool),
    parameter("autocomplete", type=bool),
)
def api_search_post(key: str, file_categories: list = None, file_extensions: list = None, file_size: list = None,
                    file_type: str = "both", page: int = 0, per_page: int = 30, lazy_search=False,
                    autocomplete: bool = False):
    """
    Search!
    :param key: the search key
    :param file_categories: unknown, documents, movies, music, images
    :param file_extensions: A list of file extensions, without the dot.
    :param file_type: files, dirs, both
    :param file_size: 2-length integer list representing the range in size as bytes
    :param page: Determines the paging
    :param per_page: Determines the amount of results
    :param lazy_search: Set to true for better search performance but less accuracy. Most suited
    for auto-complete on the front-end.
    :param autocomplete: this is the same as setting `lazy_search` to True and `per_page` to 5
    :return:
    """
    controller = SearchController()
    result = controller.search(key=key, file_categories=file_categories,
                               file_extensions=file_extensions, file_size=file_size,
                               file_type=file_type, page=page, per_page=per_page,
                               autocomplete=autocomplete, lazy_search=lazy_search)
    return result.get_json()
