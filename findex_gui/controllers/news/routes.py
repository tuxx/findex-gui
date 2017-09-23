from findex_gui.web import app, themes
from findex_gui.controllers.news.news import NewsController

@app.route("/")
def root():
    posts = NewsController.get(limit=5, offset=0)
    return themes.render("main/news", posts=posts)
