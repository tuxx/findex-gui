from findex_gui.controllers.news.news import NewsController
from findex_gui.bin.api import FindexApi, api_arg
from findex_gui.web import app


@app.route("/api/v2/news/add", methods=["POST"])
@FindexApi(
    api_arg("content", type=str, required=True, help="Post content")
)
def api_post_add(data):
    NewsController.add(data.get("content"))
    return "post added"
