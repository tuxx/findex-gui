from flask import request, session

from flask.ext.babel import gettext
from flaskext.auth.auth import get_current_user_data

from findex_gui import db, locales, auth
from findex_gui.orm.models import Users


class UserController:
    @staticmethod
    def register(username, password):
        if Users.query.filter(Users.username == username).first():
            raise Exception(gettext('User already exists'))

        user = Users(username=username, password=password)

        db.session.add(user)
        db.session.commit()

        UserController.authenticate_and_session(username=username,
                                                password=password)

        return user

    @staticmethod
    def logout():
        from flaskext.auth.auth import logout
        logout()

    @staticmethod
    def authenticate_basic(inject=False):
        """
        Authenticates the user using BASIC authentication.
        :param inject: Inject the validated user into the `request` object
        :return: orm.models.user
        """

        basic = request.authorization
        if 'username' not in basic or 'password' not in basic or not basic['username'] or not basic['password']:
            raise Exception('username/password not supplied')

        username = basic['username']
        password = basic['password']

        user = Users.query.filter(Users.username == username).one()
        if not user:
            return

        password += user.salt

        if auth.hash_algorithm(password).hexdigest() == user.password:
            if inject:
                setattr(request, 'user', user)

            return user

    @staticmethod
    def authenticate_and_session(username, password):
        try:
            user = Users.query.filter(Users.username == username).one()

            return user.authenticate(password)
        except:
            pass

    @staticmethod
    def locale_set(locale='en', user=None):
        if not locale in locales:
            raise Exception('Locale %s not found. Locales available: %s' % (locale, ', '.join(locales.keys())))

        session['locale'] = locale

        if user:
            user.locale = locale
            db.session.commit()

    @staticmethod
    def locale_get():
        locale = session.get('locale')
        if not locale:
            session['locale'] = 'en'
            return 'en'

        return locale
