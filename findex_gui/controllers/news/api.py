from findex_gui.controllers.news.news import NewsController
from flask_yoloapi import endpoint, parameter
from findex_gui.web import app


@app.route("/api/v2/news/add", methods=["POST"])
@endpoint.api(
    parameter("content", type=str, required=True)
)
def api_post_add(content):
    NewsController.add(content)
    return "post added"
