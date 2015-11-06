import bottle
from bottle import HTTPError
from findex_gui.controllers.findex.auth import basic_auth


def data_strap(f):
    """
        Decorator to fill wrapped function
        with neccesary environment data
    """
    def wrapper(self, *args):
        env = {}
        env['db_file_count'] = int(self.db.execute("""
        SELECT reltuples::int FROM pg_class WHERE relname ='files'
        """).first()[0])

        env['theme_name'] = bottle.theme.get_theme()

        if not isinstance(env, dict):
            return env
        args = (args[0], env,) if args else (env,)
        return f(self, *args)

    return wrapper


def auth_strap(f):
    """
        Decorator to auth
    """
    def wrapper(self, *args):
        env = {}

        auth = basic_auth()
        if isinstance(auth, HTTPError):
            return auth

        env['authed'] = True

        if not isinstance(env, dict):
            return env
        args = (args[0], env,) if args else (env,)
        return f(self, *args)

    return wrapper
