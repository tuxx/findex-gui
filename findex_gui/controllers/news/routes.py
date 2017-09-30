from findex_gui.web import app, themes
from findex_gui.controllers.news.news import NewsController

@app.route("/news")
def news_home():
    posts = NewsController.get(limit=10, offset=0)
    return themes.render("main/news", posts=posts)
