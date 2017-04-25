import settings
from datetime import datetime

from flask_babel import gettext
from sqlalchemy_utils import escape_like
from sqlalchemy import func
from sqlalchemy_zdb import ZdbQuery

from findex_gui import app, db
from findex_gui.orm.models import Files, Resource
from findex_common.crawl.crawl import CrawlController
from findex_common.static_variables import FileCategories, FileProtocols


class SearchController:
    @staticmethod
    def search(key: str, file_categories: list = [], file_extensions: list = [], file_size: list = [],
               file_type: str = "both", page: int = 0, per_page: int = 30,
               autocomplete: bool = False):
        """
        Search database.
        :param key: str
        :param file_categories: categories by name
        :param file_extensions: extensions by name
        :param file_size: [from,to] as bytes
        :param file_type: set to 'folder' for only folders
        :param page: offset results
        :param per_page: limit results
        :param autocomplete: indicates autocomplete was used
        :return:
        """
        now = datetime.now()
        results = SearchController._search(
            key=key,
            file_categories=file_categories,
            file_extensions=file_extensions,
            file_type=file_type,
            file_size=file_size,
            page=page,
            per_page=per_page,
            autocomplete=autocomplete)
        db_time = (datetime.now() - now).total_seconds()

        result = SearchResult(results=results)
        result.params = {
            'key': key,
            'file_categories': file_categories,
            'file_extensions': file_extensions,
            'file_type': file_type,
            'file_size': file_size,
            'page': page,
            'per_page': per_page,
            'autocomplete': autocomplete}
        result.debug["db_time"] = db_time
        return result

    @staticmethod
    def _search(**kwargs):
        kwargs['key'] = CrawlController.make_valid_key(kwargs['key'])

        # @TODO: filter by protocols / hosts
        if settings.es_enabled:
            q = ZdbQuery(Files, session=db.session)
        else:
            q = Files.query

        # only find files that are not in 'temp' mode
        # q = q.filter(Files.resource_id >= 1)

        # ignores certain filters
        ignore_filters = []

        # filter only files/dirs
        if kwargs.get("file_type"):
            if 'both'in kwargs["file_type"]:
                pass
            if 'folders' in kwargs["file_type"]:
                q = q.filter(Files.file_isdir == True)
                ignore_filters.extend(('file_size', 'file_categories', 'file_extensions'))
            elif 'files' in kwargs['file_type']:
                q = q.filter(Files.file_isdir == False)

        # size
        if kwargs['file_size'] and 'file_size' not in ignore_filters:
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

        # filter categories
        filecategories = FileCategories()

        cat_ids = []
        for cat in kwargs['file_categories']:
            cat_id = filecategories.id_by_name(cat)

            if cat_id is None:
                continue

            cat_ids.append(FileCategories().id_by_name(cat))

        if cat_ids and not 'file_categories' in ignore_filters:
            q = q.filter(Files.file_format.in_(cat_ids))

        if not kwargs['file_categories']:
            file_categories = filecategories.get_names()

        # filter extensions
        if kwargs['file_extensions'] and 'file_extensions' not in ignore_filters:
            exts = []

            for ext in kwargs['file_extensions']:
                if ext.startswith('.'):
                    ext = ext[1:]

                exts.append(ext)

            q = q.filter(Files.file_ext.in_(exts))

        # Search
        if settings.es_enabled:
            val = kwargs["key"]
        else:
            if kwargs['autocomplete'] or app.config['db_file_count'] > 5000000:
                print("warning: too many rows, enable ES")
                val = "%s%%" % escape_like(kwargs['key'])
            else:
                val = "%%%s%%" % escape_like(kwargs["key"])
        q = q.filter(Files.searchable.like(val))

        # pagination
        q = q.offset(kwargs['page'])

        if kwargs['autocomplete']:
            q = q.limit(5)
            q = q.distinct(func.lower(Files.file_name))
        else:
            q = q.limit(kwargs['per_page'])

        # fetch
        results = q.all()

        resource_ids = set([z.resource_id for z in results])
        resource_obs = {z.id: z for z in Resource.query.filter(Resource.id.in_(resource_ids)).all()}

        for result in results:
            setattr(result, 'resource', resource_obs[result.resource_id])

        results = [result.fancify() for result in results]
        return results


class SearchResult:
    def __init__(self, results):
        self.results = results
        self.params = {}
        self.debug = {}

    def to_json(self):
        return {
            "results": [z.to_json() for z in self.results],
            "params": self.params,
            "results_count": len(self.results),
            "debug": self.debug
        }
