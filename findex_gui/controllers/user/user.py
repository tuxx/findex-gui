from flask.ext.babel import gettext

from findex_gui import db, locales
from findex_gui.orm.models import Users


class UserController:
    def __init__(self, user=None):
        self.user = user

    @staticmethod
    def register(username, password):
        if Users.query.filter(Users.username == username).first():
            raise Exception(gettext('User already exists'))

        user = Users(username=username, password=password)

        db.session.add(user)
        db.session.commit()

        return user

    @staticmethod
    def login(username, password):
        try:
            user = Users.query.filter(Users.username == username).one()
            return user.authenticate(password)
        except:
            pass

    def locale_set(self, locale):
        if not locale in locales:
            raise Exception('Locale %s not found. Locales available: %s' % ', '.join(locales.keys()))

        self.user.locale = locale
        db.session.commit()