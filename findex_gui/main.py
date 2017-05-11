from findex_gui import app, themes
from findex_gui.controllers.posts.posts import PostController


@app.route("/")
def root():
    posts = PostController.get(limit=5, offset=0)
    return themes.render("main/home", posts=posts)


@app.errorhandler(404)
def error(e):
    return themes.render("main/error", msg=str(e))
