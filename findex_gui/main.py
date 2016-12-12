from findex_gui import app, themes, db

from findex_gui.orm.models import Server, Resource, ResourceMeta, ResourceGroup, User, UserGroup


@app.route('/')
def root():
    return themes.render('main/home')

@app.route("/db/remove")
def delele():
    from findex_gui.controllers.user.user import UserController

    g = db.session.query(User).first()
    db.session.delete(g)
    db.session.commit()

    v = db.session.query(UserGroup).all()
    return "ok"

@app.route("/db/test")
def testxx():
    from findex_gui.controllers.user.user import UserController

    users = db.session.query(User).all()
    u1 = users[0]
    u2 = users[1]

    g = db.session.query(UserGroup).first()
    g.admins.append(u1)
    g.admins.append(u2)

    db.session.add(g)
    db.session.commit()

    v = db.session.query(UserGroup).all()
    return "ok"

# @app.route("/db/create")
# def testxxx():
#     from findex_gui.controllers.user.user import UserController
#
#     u1 = UserController().user_add(username="test", password="test", skip_authorization=True)
#     u2 = UserController().user_add(username="test2", password="test", skip_authorization=True)
#
#     g = UserGroup(name="SuperGroep", owner=u1)
#     g.admins.append(u2)
#
#     db.session.add(g)
#     db.session.commit()
#
#     v = db.session.query(UserGroup).all()
#     return "ok"



@app.errorhandler(404)
def error(e):
    return themes.render('main/error', msg=str(e))
