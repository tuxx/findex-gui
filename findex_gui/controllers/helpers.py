import bottle
import findex_gui.controllers.findex.themes as themes


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