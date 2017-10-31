from flask_yoloapi import endpoint, parameter

from findex_gui.web import app
from findex_gui.controllers.news.news import NewsController
from findex_gui.controllers.user.decorators import admin_required

@app.route("/api/v2/news/add", methods=["POST"])
@admin_required
@endpoint.api(
    parameter("content", type=str, required=True),
    parameter("title", type=str, required=True)
)
def api_news_add(content, title):
    NewsController.add(content=content, title=title)
    return "post added"

@app.route("/api/v2/news/update", methods=["POST"])
@admin_required
@endpoint.api(
    parameter("uid", type=int, required=True),
    parameter("content", type=str, required=False),
    parameter("title", type=str, required=False)
)
def api_news_update(uid, content, title):
    NewsController.update(uid=uid, content=content, title=title)
    return "post updated"
