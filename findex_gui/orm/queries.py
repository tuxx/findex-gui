from urllib import quote

from sqlalchemy import and_, asc, desc
from findex_gui.orm.models import Files, Resource
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

    def get_resource(self, id=None, name=None, address=None, port=None, limit=None):
        query = Resource.query

        if isinstance(id, (int, long)):
            cached = self._get_cache('resources', id)
            if cached:
                return cached

            query = query.filter(Resource.id == id)

        if isinstance(address, (str, unicode)):
            cached = self._get_cache('resources', address)
            if cached:
                return cached

            query = query.filter(Resources.address == address)

        if isinstance(port, (int, long)):
            query = query.filter(Resources.port == port)

        if isinstance(name, (str, unicode)):
            query = query.filter(Resources.name == name)

        if limit and isinstance(limit, (int, long)):
            query = query.limit(limit)

        results = query.all()

        for result in results:
            #setattr(result, 'identifier', '%s:%s' % (result.address, int(result.port)))
            # wtf is this identifier shit
            self._set_cache(result)

        return results

    def get_files(self, resource_id, id=None, file_name=None, file_path=None, total_count=None, offset=None):
        """
            total_count: number of results to fetch
            offset: the offset in db
        """
        query = Files.query

        self.resource = self.get_resources(id=resource_id)

        if not file_path:
            file_path = '/'

        if self.resource.protocol in [4,5]:
            file_path = quote(file_path)

            if isinstance(file_name, (str, unicode)):
                file_name = quote(file_name)

        if id:
            _and = and_()
            _and.append(Files.id == id)
            query = query.filter(_and)
        elif isinstance(resource_id, (int, long)):
            _and = and_()
            _and.append(Files.resource_id == resource_id)
            query = query.filter(_and)

        if isinstance(file_path, (str, unicode)):
            _and = and_()
            _and.append(Files.file_path == file_path)
            query = query.filter(_and)

        if isinstance(file_name, (str, unicode)):
            _and = and_()
            _and.append(Files.file_name == file_name)
            query = query.filter(_and)

        if isinstance(total_count, (long, int)):
            query = query.limit(total_count)

        results = query.all()

        if results:
            # @TODO make relationship
            resource_ids = set([z.resource_id for z in results])
            resource_obs = {z.id: z for z in Resources.query.filter(Resources.id.in_(resource_ids)).all()}

            for result in results:
                setattr(result, 'resource', resource_obs[result.resource_id])

            results = [z.fancify() for z in results]

            return results

        return []