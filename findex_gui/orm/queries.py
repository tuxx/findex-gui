from urllib.parse import quote

from sqlalchemy import and_, asc, desc
from findex_gui.orm.models import Files, Resource, Server
from sqlalchemy.dialects import mysql, postgresql
# from findex_common.utils import DataObjectManipulation


class Queries():
    def __init__(self):
        pass


class Findex(object):
    def __init__(self):
        self.resource = None
        self._cache = {}  # @TODO: could use memcache here

    def _get_cache(self, section, id):
        if not section in self._cache:
            return

        if id in self._cache[section]:
            return self._cache[section][id]

    def _set_cache(self, item):
        key = item.__class__.__name__

        if not key in self._cache:
            self._cache[key] = {item.id: item}
        else:
            self._cache[key][item.id] = item

    def get_files(self, resource_id, id=None, file_name=None, file_path=None, total_count=None, offset=None):
        """
            total_count: number of results to fetch
            offset: the offset in db
        """
        from findex_gui.controllers.resources.resources import ResourceController
        query = Files.query

        self.resource = ResourceController.get_resources(uid=resource_id)[0]

        if not file_path:
            file_path = '/'

        if self.resource.protocol in [4, 5]:
            file_path = quote(file_path)

            if isinstance(file_name, str):
                file_name = quote(file_name)

        if id:
            _and = and_()
            _and.append(Files.id == id)
            query = query.filter(_and)
        elif isinstance(resource_id, int):
            _and = and_()
            _and.append(Files.resource_id == resource_id)
            query = query.filter(_and)

        if isinstance(file_path, str):
            _and = and_()
            _and.append(Files.file_path == file_path)
            query = query.filter(_and)

        if isinstance(file_name, str):
            _and = and_()
            _and.append(Files.file_name == file_name)
            query = query.filter(_and)

        if isinstance(total_count, int):
            query = query.limit(total_count)

        results = query.all()

        if results:
            # @TODO make relationship
            resource_ids = set([z.resource_id for z in results])
            resource_obs = {z.id: z for z in Resource.query.filter(Resource.id.in_(resource_ids)).all()}

            for result in results:
                setattr(result, 'resource', resource_obs[result.resource_id])

            results = [z.fancify() for z in results]

            return results

        return []