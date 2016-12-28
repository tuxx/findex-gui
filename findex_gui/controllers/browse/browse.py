from flask.ext.babel import gettext
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
            int(spl[1])
        except:
            raise Exception("faulty resource uid (port not integer)")

        resource = ResourceController.get_resources(address=spl[0], port=spl[1], limit=1)
        if not resource:
            raise Exception(gettext('No resource could be found for ') + resource_id)

        resource = resource[0]
        return resource

    def inspect(self, data):
        resource = self.get_resource(data['resource_id'])

        files = self.findex.get_files(
            resource_id=resource.id,
            file_path=data['path']
        )

        return files

    def browse(self, data):
        resource = self.get_resource(data['resource_id'])

        files = self.findex.get_files(
            resource_id=resource.id,
            file_path=data['path']
        )

        # sort files
        files = sorted(files, key=lambda f: f.file_name)  # alphabetically
        files = sorted(files, key=lambda f: f.file_isdir, reverse=True)  # folders always on top

        # insert CDUP
        if data['path'] != '/':
            cdup = Files(
                file_name='..',
                file_path='../',
                file_ext='',
                file_format=-1,
                file_isdir=True,
                file_modified=datetime.now(),
                file_perm=None,
                searchable=None,
                file_size=0,
                resource_id=resource.id
            )

            setattr(cdup, 'file_name_human', '..')
            files.insert(0, cdup)

        if hasattr(resource, 'meta') and resource.meta.file_distribution:
            file_distribution = OrderedDict(sorted(resource.meta.file_distribution.items(), key=lambda t: t[0]))
        else:
            file_distribution = {}

        return {
            'files': files,
            'path': data['path'],
            'resource': resource,
            'breadcrumbs': [data['resource_id']] + data['path'].split('/')[1:],
            'file_distribution': file_distribution
        }