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
    def __init__(self):
        self.db = None

        self.theme_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'themes')
        self.theme_data = {}
        self.theme_default = 'findex_official'
        self.theme_active = ''

        self.load()

    def setup_db(self, db):
        self.db = sessionmaker(bind=db.engine)()
        self.load()

    def load(self):
        if not self.db:
            return

        dirs = [os.path.join(self.theme_dir, o) for o in os.listdir(self.theme_dir) if os.path.isdir(os.path.join(self.theme_dir, o)) and not o.startswith('_')]

        for d in dirs:
            theme = self.validate_theme(d)

            if isinstance(theme, Theme):
                self.add_theme(theme)

            active_theme = self.db.query(Options).filter(Options.key == 'theme_active').first()
            if not active_theme:
                self.db.add(Options('theme_active', self.theme_default))
                self.db.commit()

                active_theme = self.theme_default
            else:
                active_theme = active_theme.val

            self.change_active_theme(active_theme)

    def add_theme(self, theme):
        self.theme_data[theme.name] = theme.options

    def validate_theme(self, dir):
        try:
            if dir in self.theme_data:
                raise Exception('Duplicate theme. Is it already added?')

            path = '%s/theme.json' % dir

            options = ''.join(utils.file_read(path))
            blob = utils.is_json(options)
            theme = Theme(name=dir, data=blob)

            return theme

        except IOError:
            raise Exception("Could not read \"%s%s\" - Themes file not found." % (self.theme_dir, path))

        except ValueError as ex:
            raise Exception("Could not parse \"%s\" - Contents not json: %s" % (path, str(ex)))

        except Exception as ex:
            raise Exception(str(ex))

    def get_theme(self):
        return self.theme_active

    def get_themes(self):
        data = []
        for k, v in self.theme_data.iteritems():
            data.append(v)

        return data

    def change_active_theme(self, theme_name):
        self.theme_active = theme_name
        self.bootstrap_theme(theme_name)

    def bootstrap_theme(self, theme_name):
        template_path = os.path.join(self.theme_dir, theme_name, 'templates')
        bottle.TEMPLATE_PATH = ['findex_gui/themes/', template_path]

        loader = jinja2.FileSystemLoader(template_path)
        jinja2.Environment(loader=loader, autoescape=True, trim_blocks=True, lstrip_blocks=True)
        import_module('findex_gui.themes.%s.bin.views' % theme_name)
