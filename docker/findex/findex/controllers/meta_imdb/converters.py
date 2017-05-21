from findex_gui.web import app
from furl import furl
from werkzeug.routing import BaseConverter
from findex_common.static_variables import PopcornParameters


class MetaImdbSearchConverter(BaseConverter):
    """The URL Converter for parsing popcorn arguments."""
    def to_python(self, value):
        lookup = PopcornParameters()

        data = {}

        for k, v in furl("?%s" % value).args.items():
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

app.url_map.converters['popcorn'] = MetaImdbSearchConverter
