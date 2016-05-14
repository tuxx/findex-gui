from json import loads

from findex_gui import app, db
from findex_gui.orm.models import Options


class OptionsController:
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