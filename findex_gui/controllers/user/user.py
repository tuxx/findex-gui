from flask.ext.babel import gettext

from findex_gui import db
from findex_gui.orm.models import Users


class UserController:
    @staticmethod
    def register(username, password):
        if Users.query.filter(Users.username == username).first():
            raise Exception(gettext('User already exists'))

        user = Users(username=username, password=password)

        db.session.add(user)
        db.session.commit()
        db.session.refresh()

        return user

    @staticmethod
    def login(username, password):
        try:
            user = Users.query.filter(Users.username == username).one()
            return user.authenticate(password)
        except:
            pass