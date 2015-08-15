from db.orm import Files, Hosts
from sqlalchemy import and_, asc, desc
from sqlalchemy.dialects import mysql
from bin.icons import Icons
from datetime import datetime
from findex_common.utils import DataObjectManipulation


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
        if isinstance(item, Hosts):
            k = 'hosts'
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

    def set_icons(self, results):
        icons = Icons()
        img_dir = '/static/img/icons/blue/128/'

        for f in results:
            setattr(f, 'img_icon', '')

            if f.file_isdir:
                if f.file_name == '..':
                    f.img_icon = img_dir + icons.additional_icons[20]
                else:
                    f.img_icon = img_dir + icons.additional_icons[21]
            elif f.file_ext in icons.additional_icons_exts:
                f.img_icon = img_dir + icons.additional_icons[icons.additional_icons_exts[f.file_ext]]
            else:
                f.img_icon = img_dir + icons.file_icons[f.file_format]

        return results

    def get_host_objects(self, id=None):
        query = self.db.query(Hosts)

        cached = self._get_cache('hosts', id)
        if cached:
            return cached

        if isinstance(id, (int, long)):
            query = query.filter(Hosts.id == id)

        result = query.first()
        self._set_cache(result)

        return result

    def get_files_objects(self, id=None, host_id=None, file_path=None, total_count=None, offset=None):
        """
            total_count: number of results to fetch
            offset: the offset in db
        """
        query = self.db.query(Files)

        if id:
            _and = and_()
            _and.append(Files.id == id)
            query = query.filter(_and)
        elif isinstance(host_id, (int, long)):
            _and = and_()
            _and.append(Files.host_id == host_id)
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
