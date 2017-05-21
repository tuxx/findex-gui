from flask_babel import gettext
from collections import OrderedDict
from datetime import datetime

from findex_gui.orm.queries import Findex
from findex_gui.orm.models import Files
from findex_gui.controllers.resources.resources import ResourceController


class Browse:
    def __init__(self):
        self.findex = Findex()

    def get_resource(self, resource_id):
        """
        :param resource_id: Should be a concat of `server.address:resource.port`
        :return: `Resource`, raise exception when non found
        """
        spl = resource_id.split(":", 1)
        if not spl[0] or not spl[1]:
            raise Exception("faulty resource uid")

        try:
            spl[1] = int(spl[1])
        except:
            raise Exception("faulty resource uid (port not integer)")

        resource = ResourceController.get_resources(address=spl[0], port=spl[1], limit=1)
        if not resource:
            raise Exception(gettext("No resource could be found for ") + resource_id)

        resource = resource[0]
        return resource

    def get_file(self, resource, file_path, file_name, file_ext):
        f = self.findex.get_files(resource_id=resource.id,
                                  file_path=file_path,
                                  file_name=file_name,
                                  file_ext=file_ext)
        try:
            return f[0]
        except:
            raise Exception("file could not be found")

    def inspect(self, data):
        resource = self.get_resource(data["resource_id"])
        files = self.findex.get_files(
            resource_id=resource.id,
            file_path=data["path"]
        )

        return files

    def browse(self, resource, path, filename):
        files = self.findex.get_files(
            resource_id=resource.id,
            file_path=path
        )

        # sort files
        files = sorted(files, key=lambda f: f.file_name)  # alphabetically
        files = sorted(files, key=lambda f: f.file_isdir, reverse=True)  # folders always on top

        # insert CDUP
        if path != "/":
            cd_up = Files(
                file_name="..",
                file_path="../",
                file_ext="",
                file_format=-1,
                file_isdir=True,
                file_modified=datetime.now(),
                file_perm=None,
                searchable=None,
                file_size=0,
                resource_id=resource.id)
            files.insert(0, cd_up)

        file_distribution = {}
        if hasattr(resource, "meta") and resource.meta.file_distribution:
            file_distribution = OrderedDict(sorted(list(
                resource.meta.file_distribution.items()), key=lambda t: t[0]))

        return {
            "files": files,
            "path": path,
            "resource": resource,
            "breadcrumbs": [resource.server.name] + path.split("/")[1:],
            "file_distribution": file_distribution
        }
