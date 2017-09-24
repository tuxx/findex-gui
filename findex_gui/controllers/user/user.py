from flask import request, session

from findex_gui.controllers.auth.auth import get_current_user_data, logout
from findex_gui.web import db, locales, auth
from findex_gui.orm.models import User, UserGroup
from findex_gui.controllers.user.roles import default_registered_roles, role_req, check_role
from findex_common.exceptions import DatabaseException, FindexException, RoleException, AuthenticationException


class UserController:
    @staticmethod
    def user_view(uid: int = None, username: str = None, log_error: bool = True):
        """
        Returns an user.
        :param uid: user id
        :param username: username
        :param log_error: to stderr on exception
        :return: user
        """
        if uid:
            _filter = {"id": uid}
        else:
            _filter = {"username": username}

        try:
            return db.session.query(User).filter_by(**_filter).first()
        except Exception as ex:
            db.session.rollback()
            raise DatabaseException(ex, log_error)

    @staticmethod
    @role_req("USER_REGISTERED", "USER_DELETE")
    def user_delete(username: str, log_error: str = True):
        """
        Deletes an user.
        :param username: username
        :param log_error: to stderr on exception
        :return: returns True if successful
        """
        try:
            user = db.session.query(User).filter(
                User.username == username).first()
            if not user:
                return False

            db.session.delete(user)
            db.session.commit()
            db.session.flush()
            return True
        except Exception as ex:
            db.session.rollback()
            raise DatabaseException(ex, log_error)

    @staticmethod
    @role_req("USER_CREATE")
    def user_add(username, password, admin=False, removable=True,
                 privileges=default_registered_roles, create_session=False,
                 log_error=True, ignore_constraint_conflict=False, **kwargs):
        """
        Adds an user.
        :param username: username
        :param password: password
        :param admin: is administrator
        :param removable: persistent user or not
        :param privileges:
        :param create_session: registers this login with a web session
        :param log_error: to stderr on exception
        :param ignore_constraint_conflict: ignores database constraint errors (postgres only)
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
            db.session.flush()
            if create_session:
                UserController.authenticate_and_session(username=username,
                                                        password=password)
            return user
        except Exception as ex:
            db.session.rollback()
            raise DatabaseException(ex, log_error)

    @staticmethod
    @role_req("USER_REGISTERED", "CREATE_USER_GROUP")
    def group_add(name, owner, **kwargs):
        group = UserGroup(name=name, owner=owner)
        db.session.add(group)
        db.session.commit()
        db.session.flush()
        return group

    @staticmethod
    def logout():
        """
        Logs the user out.
        :return:
        """
        logout()

    @staticmethod
    def authenticate_basic(inject=False):
        """
        Authenticates the user using BASIC authentication
        :param inject: Inject the validated user into the `request` object
        :return: orm.models.user
        """
        if not hasattr(request, "authorization"):
            raise FindexException("request object has no attribute authorization")
        bauth = request.authorization
        if "username" not in bauth or "password" not in bauth or not bauth["username"] or not bauth["password"]:
            raise FindexException("username/password not supplied")

        username = bauth["username"]
        password = bauth["password"]

        try:
            user = User.query.filter(User.username == username).one()
            if not user:
                raise AuthenticationException("bad username/password combination")
        except Exception as e:
            raise AuthenticationException("bad username/password combination")

        password += user.salt
        if auth.hash_algorithm(password.encode("UTF-8")).hexdigest() == user.password:
            if inject:
                setattr(request, "user", user)
            return user
        else:
            raise AuthenticationException("bad username/password combination")

    @staticmethod
    def authenticate_and_session(username: str, password: str):
        """
        Authenticate and session.
        :param username: username
        :param password: password
        :return:
        """
        try:
            user = UserController.user_view(username=username)
            return user.authenticate(password)
        except:
            pass

    @staticmethod
    def locale_set(locale: str ="en", user_id: id = None):
        """
        Sets the web interface locale.
        :param locale: The language as "en" or "nl", etc.
        :param user_id: user uid
        :return:
        """
        if locale not in locales:
            raise Exception("Locale %s not found. Locales available: %s" % (locale, ", ".join(list(locales.keys()))))

        session["locale"] = locale
        if user_id:
            user = UserController.user_view(uid=user_id)
            user.locale = locale
            db.session.commit()
            db.session.flush()

    @staticmethod
    def locale_get():
        """
        Gets the web interface locale. Defaults to "en".
        :return:
        """
        locale = session.get("locale")
        if not locale:
            session["locale"] = "en"
            return "en"
        return locale

    @staticmethod
    def get_current_user(apply_timeout: bool = True):
        """
        The same as calling `get_current_user_data` except that
        this returns the user.
        :return: user
        """
        user = get_current_user_data(apply_timeout)
        if user:
            user = UserController.user_view(uid=user["id"])
        else:
            try:
                user = UserController.authenticate_basic()
            except AuthenticationException as e:
                raise e
            except Exception as e:
                pass
            if not user:
                user = UserController.user_view(username="anon")  # assign the default anonymous role
                if not user:
                    raise RoleException("User anon not found")
        if isinstance(user, DatabaseException):
            raise user
        return user

    @staticmethod
    def is_admin():
        """
        Utility function to check if the current user
        (from session) is admin.
        :return: bool
        """
        data = get_current_user_data()
        if data is None:
            return
        return data["admin"] == True
