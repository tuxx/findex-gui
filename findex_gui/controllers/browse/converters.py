from findex_gui import app
from furl import furl
from werkzeug.routing import BaseConverter


class BrowseUrlConverter(BaseConverter):
    regex = '[^/].*?'
    weight = 666

    def to_python(self, value):
        value = value.split('/')
        if not len(value) >= 2:
            return

        data = {
            'resource_id': value[0],
            'path': '/'.join(value[1:])
        }

        if not data['path'].startswith('/'):
            data['path'] = '/' + data['path']

        return data

    def to_url(self, values):
        return '+'.join(BaseConverter.to_url(value)
                        for value in values)

app.url_map.converters['browse'] = BrowseUrlConverter