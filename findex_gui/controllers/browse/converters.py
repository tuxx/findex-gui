from findex_gui import app
from furl import furl
from werkzeug.routing import BaseConverter


class BrowseUrlConverter(BaseConverter):
    regex = "[^/].*?"
    weight = 666

    def to_python(self, value):
        value = value.split("/")
        if not len(value) >= 1:
            return Exception("faulty path")

        data = {
            "resource_id": value[0],
            "path": "/".join(value[1:])
        }

        if not data["path"].startswith("/"):
            data["path"] = "/" + data["path"]

        if ":" not in data["resource_id"]:
            return Exception("faulty resource uid")

        return data

    def to_url(self, values):
        return "+".join(BaseConverter.to_url(value)
                        for value in values)

app.url_map.converters["browse"] = BrowseUrlConverter