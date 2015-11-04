from importlib import import_module

from sqlalchemy import and_, asc, desc
from sqlalchemy.dialects import mysql, postgresql

from findex_gui.db.orm import Files, Resources
from findex_common.utils import DataObjectManipulation

import findex_gui.controllers.findex.themes as themes


class Findex(object):
    def __init__(self, db):
        self.db = db
        self._cache = {}

    def _get_cache(self, section, id):
        if not section in self._cache:
            return

        if id in self._cache[section]:
            return self._cache[section][id]

    def _set_cache(self, item):
        if isinstance(item, Resources):
            k = 'resources'
        elif isinstance(item, Files):
            k = 'files'
        else:
            return

        if not k in self._cache:
            self._cache[k] = {item.id: item}
        else:
            self._cache[k][item.id] = item

    def set_humanize(self, results):
        for f in results:
            f = DataObjectManipulation(f).humanize(humandates=True, humanpath=True, humansizes=True, dateformat="%d %b %Y")

            file_url = '%s%s' % (f.file_path_human, f.file_name_human)
            setattr(f, 'file_url', file_url)
        return results

    def set_icons(self, env, files):
        try:
            theme_icon_module = import_module('static.themes.%s.bin.icons' % env['theme_name'])
            return theme_icon_module.set_icons(env=env, files=files)
        except Exception as ex:
            for f in files:
                f.img_icon = '/static/img/error.png'

        return files

    def get_resource_objects(self, id=None):
        query = self.db.query(Resources)

        if isinstance(id, (int, long)):
            cached = self._get_cache('resources', id)
            if cached:
                return cached

            query = query.filter(Resources.id == id)

        result = query.all()
        if len(result) == 1:
            result = result[0]

        self._set_cache(result)

        return result

    def get_files_objects(self, id=None, resource_id=None, file_path=None, total_count=None, offset=None):
        """
            total_count: number of results to fetch
            offset: the offset in db
        """
        query = self.db.query(Files)

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

        if isinstance(total_count, (long, int)):
            query = query.limit(total_count)
        
        results = query.all()

        if results:
            results = self.set_humanize(results)
            return results

        return []
