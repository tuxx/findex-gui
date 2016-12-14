from flask import request, session
from flaskext.auth.auth import get_current_user_data

from findex_gui import db, locales, auth
from findex_gui.orm.models import User, UserGroup
from findex_gui.controllers.user.roles import default_anon_roles, Role
from findex_common.exceptions import DatabaseException


def check_role(requirements, **kwargs):
    if "skip_authorization" not in kwargs:
        try:
            user = get_current_user_data()
            if user is None:
                user = UserController.user_view(username="anon")
            if not user:
                raise Exception("forbidden")
        except Exception:
            raise Exception("forbidden")

        for requirement in requirements:
            roles = [r.name for r in user.roles]
            if requirement not in roles:
                raise Exception("Forbidden")


def role_req(*requirements):
    def wrap(f):
        def wrapped_f(*args, **kwargs):
            check_role(requirements, **kwargs)
            return f(*args, **kwargs)
        return wrapped_f
    return wrap


class UserController:
    @staticmethod
    def user_view(uid=None, username=None):
        """
        Returns an user
        :param uid: user id
        :param username: username
        :return: user
        """
        if uid:
            _filter = {"id": uid}
        else:
            _filter = {"username": username}

        try:
            user = db.session.query(User).filter_by(**_filter).first()
            return user
        except Exception as ex:
            db.session.rollback()
            return DatabaseException(ex)

    @staticmethod
    @role_req("REGISTERED", "USER_DELETE")
    def user_delete(username):
        """
        Deletes an user
        :param username: username
        :return: returns True if successful
        """
        try:
            user = db.session.query(User).filter(
                User.username == username).first()
            if not user:
                return False

            db.session.delete(user)
            db.session.commit()
            return True
        except Exception as ex:
            db.session.rollback()
            return DatabaseException(ex)

    @staticmethod
    @role_req("USER_CREATE")
    def user_add(username, password, admin=False, removable=True,
                 privileges=default_anon_roles, create_session=False, **kwargs):
        """
        Adds an user
        :param username: username
        :param password: password
        :param admin: is administrator
        :param removable: persistent user or not
        :param privileges:
        :param create_session: registers this login with a web session
        :return: returns the newly added user
        """
        user = User(username=username, password=password)
        user.roles = privileges
        user.removable = removable

        if admin:
            check_role("CREATE_USER_ADMIN", **kwargs)
            user.admin = admin

        try:
            db.session.add(user)
            db.session.commit()
            if create_session:
                UserController.authenticate_and_session(username=username,
                                                        password=password)
            return user
        except Exception as ex:
            db.session.rollback()
            return DatabaseException(ex)

    @staticmethod
    @role_req("REGISTERED", "CREATE_USER_GROUP")
    def group_add(name, owner, **kwargs):
        group = UserGroup(name=name, owner=owner)
        db.session.add(group)
        db.session.commit()
        return group

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

        user = User.query.filter(User.username == username).one()
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
            user = User.query.filter(User.username == username).one()
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

    @staticmethod
    def get_current_user_data(apply_timeout=True):
        data = get_current_user_data(apply_timeout)
        if data:
            e = ""

    @staticmethod
    def is_admin():
        data = get_current_user_data()
        if data is None:
            return

        elif not data['admin']:
            return

        return True