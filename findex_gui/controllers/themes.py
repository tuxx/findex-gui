import os
from flask import render_template
from findex_gui import db, app
from findex_gui.orm.models import Options
from findex_gui.controllers.options.options import OptionsController
from findex_common import utils


class Theme:
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
                raise Exception("Theme error for \"%s\". Option \"%s\" not found in theme configuration file but should be present." % (self.name, option))

        for k, v in data.iteritems():
            self.options[k] = v


class ThemeController:
    def __init__(self):
        self.base = app.config['dir_base'] + '/themes/'
        self.data = {}

    def render(self, template_path, status_code=200, **kwargs):
        # check session theme here
        theme = self.get_active()

        kwargs['env'] = {z: app.config[z] for z in app.config if z.islower()}

        return render_template('%s/templates/%s.html' % (theme, template_path), **kwargs), status_code

    def get_active(self):
        return OptionsController.theme_get_active()

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

    def _validate(self, theme_name):
        path = ''

        try:
            if theme_name in self.data:
                raise Exception('Duplicate theme. Is it already added?')

            path = '%s/theme.json' % theme_name

            options = ''.join(utils.file_read(path))
            blob = utils.is_json(options)
            theme_name = Theme(name=theme_name, data=blob)

            return theme_name

        except IOError:
            raise Exception("Could not read \"%s%s\" - Themes file not found." % (self.base, path))

        except ValueError as ex:
            raise Exception("Could not parse \"%s\" - Contents not json: %s" % (path, str(ex)))

        except Exception as ex:
            raise Exception(str(ex))