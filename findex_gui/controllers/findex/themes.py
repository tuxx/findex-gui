import os, jinja2, bottle
from datetime import datetime
from importlib import import_module

from sqlalchemy.orm import sessionmaker

from findex_gui.db.orm import Options
from findex_common import utils
from findex_common.exceptions import ThemeException


class Theme():
    def __init__(self, name, data):
        self.name = name
        self.options = {}

        self.validate(data)

    def __getitem__(self, item):
        return self.options[item]

    def validate(self, data):
        options = [
            "author",
            "author_url",
            "theme_name",
            "theme_version",
            "theme_description"
        ]

        for option in options:
            if not option in data:
                raise ThemeException("Error parsing a needed option from theme \"%s\". Option \"%s\" not found in theme configuration file but should be present." % (self.name, option))

        for k, v in data.iteritems():
            self.options[k] = v


class Themes():
    def __init__(self, db):
        self.db = sessionmaker(bind=db.engine)()
        self.theme_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'themes')
        self.themes = {}

        self.active_theme = {}

        self.load()

    def load(self):
        dirs = os.listdir(self.theme_dir)
        for d in [z for z in dirs if not z.startswith('_')]:
            self.validate_dir(d)

        active_theme = self.get_theme()
        if not active_theme:
            self.change_theme('findex_official')
        else:
            self.change_theme(active_theme.val)

    def validate_dir(self, dir):
        try:
            if dir in self.themes:
                raise Exception('Duplicate theme. Is it already added?')

            path = '%s/%s/theme.json' % (self.theme_dir, dir)

            options = ''.join(utils.file_read(path))
            blob = utils.is_json(options)

            theme = Theme(name=dir, data=blob)
            self.themes[theme['theme_name']] = theme.options

        except IOError:
            raise Exception("Could not read \"%s%s\" - Themes file not found." % (self.theme_dir, path))

        except ValueError as ex:
            raise Exception("Could not parse \"%s\" - Contents not json: %s" % (path, str(ex)))

        except Exception as ex:
            raise Exception(str(ex))

    def get_theme(self):
        if self.active_theme:
            if (datetime.now() - self.active_theme['date']).total_seconds() <= 300:
                return self.active_theme['name']

        return self.db.query(Options).filter(Options.key == 'theme_active').first()

    def change_theme(self, name):
        theme = self.get_theme()

        if not theme:
            self.db.add(Options(key='theme_active', val=name))
            self.db.commit()
        elif theme.val != name:
            theme.val = name
            self.db.commit()

        template_path = os.path.join(self.theme_dir, name, 'templates')
        bottle.TEMPLATE_PATH = [template_path]
        loader = jinja2.FileSystemLoader(template_path)
        jinja2.Environment(loader=loader, autoescape=True, trim_blocks=True, lstrip_blocks=True)
        import_module('findex_gui.static.themes.%s.bin.views' % name)

        self.active_theme = {'name': name, 'date': datetime.now()}


DATA = None