from urllib.parse import quote

from findex_gui.orm.models import Files, Resource


class Findex(object):
    def __init__(self):
        self.resource = None
        self._cache = {}

    def _get_cache(self, section, _id):
        if section not in self._cache:
            return

        if _id in self._cache[section]:
            return self._cache[section][_id]

    def _set_cache(self, item):
        key = item.__class__.__name__

        if key not in self._cache:
            self._cache[key] = {item.id: item}
        else:
            self._cache[key][item.id] = item

    def get_files(self, resource_id: int, _id: int = None,
                  file_name: str = None, file_path: str = None,
                  limit: int = None, offset: int = None,
                  file_ext: str = None):
        """
        :param resource_id:
        :param _id:
        :param file_name:
        :param file_path:
        :param limit:
        :param offset:
        :param file_ext:
        :return: list of `Files` objects
        """
        from findex_gui.controllers.resources.resources import ResourceController
        q = Files.query

        self.resource = ResourceController.get_resources(uid=resource_id)[0]

        if not file_path:
            file_path = "/"

        # ??
        if self.resource.protocol in [4, 5]:
            file_path = quote(file_path)
            if isinstance(file_name, str):
                file_name = quote(file_name)

        if _id:
            q = q.filter(Files.id == _id)
        elif isinstance(resource_id, int):
            q = q.filter(Files.resource_id == resource_id)
        if isinstance(file_path, str):
            q = q.filter(Files.file_path == file_path)
        if isinstance(file_name, str):
            q = q.filter(Files.file_name == file_name)
        if isinstance(file_ext, str):
            if file_ext.startswith("."):
                file_ext = file_ext[1:]
            q = q.filter(Files.file_ext == file_ext)
        if isinstance(limit, int):
            q = q.limit(limit)
        results = q.all()

        if results:
            if resource_id is None:
                resource_ids = set([z.resource_id for z in results])
                resource_obs = {z.id: z for z in Resource.query.filter(Resource.id.in_(resource_ids)).all()}

                for result in results:
                    setattr(result, 'resource', resource_obs[result.resource_id])
            else:
                for result in results:
                    setattr(result, "resource", self.resource)

            return results

        return []
