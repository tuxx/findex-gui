from findex_gui import app
from furl import furl
from werkzeug.routing import BaseConverter
from findex_common.static_variables import SearchParameters


class SearchUrlConverter(BaseConverter):
    """
    The URL Converter for parsing search arguments.
    Example: /search/die%20hard&cats=[movies]&type=[files]&size=0-1823718372
    """
    def to_python(self, value):
        lookup = SearchParameters()

        if value.startswith('key='):
            value = value[4:]

        data = {}

        for k, v in furl('/?key='+value).args.items():
            kk = lookup.id_by_name(k)
            if kk:
                k = kk

            if v.startswith('[') and v.endswith(']'):
                v = v[1:-1]

                v = v.split(',')
                vv = []

                for elem in v:
                    try:
                        vv.append(int(elem))
                    except ValueError:
                        vv.append(elem)

                data[k] = vv
            else:
                try:
                    data[k] = int(v)
                except ValueError:
                    data[k] = v

        return data

    def to_url(self, values):
        return '+'.join(BaseConverter.to_url(value)
                        for value in values)

app.url_map.converters['search'] = SearchUrlConverter
