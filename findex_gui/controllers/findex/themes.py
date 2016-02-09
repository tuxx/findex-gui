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


class ThemeController():
    def __init__(self, db):
        self.db = db
        self.base = os.path.join(os.path.dirname(__file__), '..', '..', 'themes')
        self.data = {}
        self.active = ''

    def loop(self):
        self.all()

        active_theme = self.db.query(Options).filter(Options.key == 'theme_active').first()
        theme_name = 'findex_official'
        if not active_theme:
            self.db.add(Options('theme_active', theme_name))
            self.db.commit()
        else:
            theme_name = active_theme.val

        self.set(theme_name)

    def set(self, theme_name):
        if not theme_name in self.data:
            return False

        if theme_name == self.active and self.active != '':
            return False

        theme = self.db.query(Options).filter(Options.key == 'theme_active').first()
        if not theme:
            self.db.add(Options('theme_active', theme_name))
            self.db.commit()
        else:
            theme.val = theme_name
            self.db.commit()

        self.active = theme_name
        self._bootstrap(theme_name)

        self.all()
        return True

    def all(self):
        dirs = [os.path.join(self.base, o) for o in os.listdir(self.base) if os.path.isdir(os.path.join(self.base, o)) and not o.startswith('_')]

        data = []
        for d in dirs:
            try:
                theme = self._validate(d)
            except:
                continue

            if isinstance(theme, Theme):
                data.append(theme)

        for d in data:
            self.data[d.options['theme_name']] = d.options

    def _validate(self, dir):
        try:
            if dir in self.data:
                raise Exception('Duplicate theme. Is it already added?')

            path = '%s/theme.json' % dir

            options = ''.join(utils.file_read(path))
            blob = utils.is_json(options)
            theme = Theme(name=dir, data=blob)

            return theme

        except IOError:
            raise Exception("Could not read \"%s%s\" - Themes file not found." % (self.base, path))

        except ValueError as ex:
            raise Exception("Could not parse \"%s\" - Contents not json: %s" % (path, str(ex)))

        except Exception as ex:
            raise Exception(str(ex))

    def _bootstrap(self, theme_name):
        template_path = os.path.join(self.base, theme_name, 'templates')
        bottle.TEMPLATE_PATH = ['findex_gui/themes/', template_path]

        loader = jinja2.FileSystemLoader(template_path)
        jinja2.Environment(loader=loader, autoescape=True, trim_blocks=True, lstrip_blocks=True)
        import_module('findex_gui.themes.%s.bin.views' % theme_name)
