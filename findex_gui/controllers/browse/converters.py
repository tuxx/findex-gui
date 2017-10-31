import os
import ntpath

from findex_gui.web import app
from findex_gui.controllers.browse.browse import Browse
from furl import furl
from werkzeug.routing import BaseConverter


class BrowseUrlConverter(BaseConverter):
    regex = "[^/].*?"
    weight = 666

    def to_python(self, value):
        file_name = None
        file_ext = None
        file_isdir = value.endswith("/")

        value = value.split("/")
        if not len(value) >= 1:
            raise Exception("faulty path")

        resource_id = value[0]
        path = "/".join(value[1:])

        if not path.startswith("/"):
            path = "/%s" % path

        if ":" not in resource_id:
            raise Exception("faulty resource uid")
        try:
            resource = Browse().get_resource(resource_id=resource_id)
        except:
            raise Exception("resource not found")

        if not file_isdir:
            file_name, file_ext = os.path.splitext(ntpath.basename(path))
            if not file_ext:
                file_ext = None

        file_path = "%s/" % "/".join(path.split("/")[:-1])

        f = None
        if file_path and file_name:
            try:
                f = Browse().get_file(resource=resource,
                                      file_name=file_name,
                                      file_path=file_path,
                                      file_ext=file_ext)
            except Exception as ex:
                raise Exception("file not found")

        return resource, f, file_path, file_name

    def to_url(self, values):
        return "+".join(BaseConverter.to_url(value)
                        for value in values)

app.url_map.converters["browse"] = BrowseUrlConverter
