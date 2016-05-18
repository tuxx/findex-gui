from collections import OrderedDict
from datetime import datetime

from findex_gui.orm.queries import Findex
from findex_gui.orm.models import Files


class Browse:
    def __init__(self):
        self.findex = Findex()

    def get_resource(self, resource_id):
        """
        :param resource_id: Can either be a `Resources.id` or `Resources.name`
        :return: `Resource`
        """
        try:
            return self.findex.get_resources(id=int(resource_id), limit=1)
        except:
            pass

        resource = self.findex.get_resources(name=resource_id, limit=1)
        if resource:
            return resource

        raise Exception('No resource could be found for \"%s\"' % resource_id)

    def inspect(self, data):
        resource = self.get_resource(data['resource_id'])

        files = self.findex.get_files(
            resource_id=resource.id,
            file_path=data['path']
        )

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

        if resource.meta.file_distribution:
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