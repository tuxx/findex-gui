from json import loads
from flask.ext.babel import gettext

from findex_gui import app, db
from findex_gui.orm.models import Options


class OptionsController:
    @staticmethod
    def get(key):
        return Options.query.filter(Options.key == key).first()

    @staticmethod
    def set(key, val):
        option = Options.query.filter(Options.key == key).first()

        if key == 'theme_active':
            if not val in themes.data:
                raise Exception(gettext('theme name \'%s\' not found' % val))

        if option:
            option.val = val
            db.session.commit()
        else:
            db.session.add(Options(key=key, val=val))

    @classmethod
    def theme_get_active(cls):
        theme = Options.query.filter(Options.key == 'theme_active').first()

        if not theme:
            theme = cls.theme_set_default()

        return theme.val['theme']

    @classmethod
    def theme_set_default(cls):
        theme = Options.query.filter(Options.key == 'theme_active').first()
        if theme:
            db.session.delete(theme)

        theme = Options(key='theme_active', val={'theme': 'bucket'})

        db.session.add(theme)
        db.session.commit()

        return theme