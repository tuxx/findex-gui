import os
from sqlalchemy_utils import escape_like
from sqlalchemy import func
from findex_gui import app
from findex_gui.orm.models import Files, Resources
from findex_common.static_variables import FileCategories, FileProtocols
from findex_common.utils import Sanitize

import json


class SearchResult:
    def __init__(self):
        self.results = []
        self.params = {}

    def to_dict(self):
        blob = {
            'results': [z.to_dict() for z in self.results],
            'params': self.params,
            'results_count': len(self.results)
        }

        return blob


class SearchController:
    # @TODO: should call this instead, let it determine what class to use
    def __init__(self):
        self._iface = self._get_iface()

    def _get_iface(self):
        return DatabaseSearchController

    # /search/die%20hard&cats=[unknown,documents,movies,music,pictures]&proto=[ftp,http,smb]&type=both&size=134217728-536870912&exts=[mp3]
    def search(self, key, file_categories=[], file_extensions=[], file_size=[], file_type='both', page=0, per_page=30,
               autocomplete=False, lazy_search=False, **kwargs):

        result_obj = SearchResult()
        result_obj.results = self._iface.search(key=key,
                                                file_categories=file_categories,
                                                file_extensions=file_extensions,
                                                file_type=file_type,
                                                file_size=file_size,
                                                page=page,
                                                per_page=per_page,
                                                autocomplete=autocomplete,
                                                lazy_search=lazy_search)

        result_obj.params = {
            'key': key,
            'file_categories': file_categories,
            'file_extensions': file_extensions,
            'file_type': file_type,
            'file_size': file_size,
            'page': page,
            'per_page': per_page,
            'autocomplete': autocomplete
        }

        return result_obj


class DatabaseSearchController:
    @staticmethod
    def search(**kwargs):
        kwargs['key'] = DatabaseSearchController.clean_and_validate_key(kwargs['key'])

        # @TODO: filter by protocols / hosts: http://stackoverflow.com/a/6226740/2054778  - make a relation
        q = Files.query

        # ignores certain filters
        ignore_keys = []

        #
        # filter only files/dirs, or both
        #
        if 'folders' in kwargs['file_type'] and 'files' in kwargs['file_type']:
            pass
        elif 'folders' in kwargs['file_type']:
            q = q.filter(Files.file_isdir == True)

            # When searching only for directories, ignore filters that are not relevant
            ignore_keys.extend(('file_size', 'file_categories', 'file_extensions'))
        elif 'files' in kwargs['file_type']:
            q = q.filter(Files.file_isdir == False)

        #
        # size
        #
        if kwargs['file_size'] and not 'file_size' in ignore_keys:
            try:
                file_size = kwargs['file_size'].split('-')

                if not len(file_size) == 2:
                    raise Exception()

                if file_size[0] == '*':
                    q = q.filter(Files.file_size <= int(file_size[1]))
                elif file_size[1] == '*':
                    q = q.filter(Files.file_size >= int(file_size[0]))
                else:
                    q = q.filter(Files.file_size.between(*[int(x) for x in file_size]))
            except:
                pass

        #
        # filter categories
        #
        filecategories = FileCategories()

        cat_ids = []
        for cat in kwargs['file_categories']:
            cat_id = filecategories.id_by_name(cat)

            if cat_id is None:
                continue

            cat_ids.append(FileCategories().id_by_name(cat))

        if cat_ids and not 'file_categories' in ignore_keys:
            q = q.filter(Files.file_format.in_(cat_ids))

        if not kwargs['file_categories']:
            file_categories = filecategories.get_names()

        #
        # filter extensions
        #
        if kwargs['file_extensions'] and not 'file_extensions' in ignore_keys:
            exts = []

            for ext in kwargs['file_extensions']:
                if ext.startswith('.'):
                    ext = ext[1:]

                exts.append(ext)

            q = q.filter(Files.file_ext.in_(exts))

        #
        # Search
        if kwargs['autocomplete'] or kwargs['lazy_search'] or app.config['db_file_count'] > 5000000:
            q = q.filter(Files.searchable.like(escape_like(kwargs['key']) + '%'))
        else:
            q = q.filter(Files.searchable.like('%' + escape_like(kwargs['key']) + '%'))

        #
        # pagination
        q = q.offset(kwargs['page'])

        if kwargs['autocomplete']:
            q = q.limit(5)
            q = q.distinct(func.lower(Files.file_name))
        else:
            q = q.limit(kwargs['per_page'])

        #
        # fetch
        results = q.all()

        # @TODO make relationship
        resource_ids = set([z.resource_id for z in results])
        resource_obs = {z.id: z for z in Resources.query.filter(Resources.id.in_(resource_ids)).all()}

        for result in results:
            setattr(result, 'resource', resource_obs[result.resource_id])

        results = [result.fancify() for result in results]

        return results

    @staticmethod
    def clean_and_validate_key(key):
        # `Files.searchable` does not have any of these characters, strip them.
        for clean in ['-', ',', '+', '_', '%']:
            key = key.replace(clean, ' ')

        if len(key) <= 1:
            raise Exception('Search key too short')

        return key.lower()
