import ntpath

from findex_gui import app
from findex_gui.controllers.browse.browse import Browse
from furl import furl
from werkzeug.routing import BaseConverter


class BrowseUrlConverter(BaseConverter):
    regex = "[^/].*?"
    weight = 666

    def to_python(self, value):
        value = value.split("/")
        if not len(value) >= 1:
            return Exception("faulty path")

        resource_id = value[0]
        path = "/".join(value[1:])

        if not path.startswith("/"):
            path = "/%s" % path

        if ":" not in resource_id:
            return Exception("faulty resource uid")

        filename = ntpath.basename(path)
        path = "%s/" % "/".join(path.split("/")[:-1])

        try:
            resource = Browse().get_resource(resource_id=resource_id)
        except:
            return Exception("resource not found")

        f = None
        if path and filename:
            try:
                f = Browse().get_file(resource=resource, file_name=filename, file_path=path)
            except:
                return Exception("file not found")

        return resource, f, path, filename

    def to_url(self, values):
        return "+".join(BaseConverter.to_url(value)
                        for value in values)

app.url_map.converters["browse"] = BrowseUrlConverter