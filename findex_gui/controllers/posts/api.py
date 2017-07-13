import flask

from datetime import datetime
from findex_gui.controllers.posts.posts import PostController
from findex_gui.bin.api import FindexApi, api_arg
from findex_gui.orm.queries import Findex
from findex_gui.web import app, locales


@app.route("/api/v2/post/add", methods=["POST"])
@FindexApi(
    api_arg("content", type=str, required=True, help="Post content")
)
def api_post_add(data):
    PostController.add(data.get("content"))
    return "post added"
