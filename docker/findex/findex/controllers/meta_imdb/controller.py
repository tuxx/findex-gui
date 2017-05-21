from typing import List

from findex_gui.web import db
from findex_gui.orm.models import MetaImdb, MetaImdbActors, MetaImdbDirectors, Files
from findex_common.exceptions import SearchException

from sqlalchemy import desc
from sqlalchemy_zdb import ZdbQuery
from sqlalchemy_zdb.types import ZdbLiteral


class MetaImdbController:
    @staticmethod
    def get(imdb_id):
        return db.session.query(MetaImdb).filter(MetaImdb.id == imdb_id).first()

    @staticmethod
    def get_director(search=None):
        """A faster SELECT DISTINCT unnest(director) FROM meta_imdb
            using meta_imdb_directors
        """
        q = ZdbQuery(MetaImdbDirectors, session=db.session)
        if search:
            search = search.replace("*", "")
            if not isinstance(search, str):
                raise SearchException("search must be str")
            q = q.filter(MetaImdbDirectors.director.like(ZdbLiteral("%s*" % search)))
        results = q.all()
        return results

    @staticmethod
    def get_actors(search=None):
        """A faster SELECT DISTINCT unnest(actors) FROM meta_imdb
            using meta_imdb_actors
        """
        q = ZdbQuery(MetaImdbActors, session=db.session)
        if search:
            search = search.replace("*", "")
            if not isinstance(search, str):
                raise SearchException("search must be str")
            q = q.filter(MetaImdbActors.actor.like(ZdbLiteral("%s*" % search)))
        results = q.all()
        return results

    @staticmethod
    def get_actor_played_in(actor):
        """Returns a list of movies given an actor/actress"""

        q = ZdbQuery(MetaImdb, session=db.session)
        q = q.filter(MetaImdb.actors.like(actor))
        results_imdb = q.all()
        if not results_imdb:
            return {
                "local": [],
                "imdb": []
            }

        ids = [z.id for z in results_imdb]
        results_imdb = sorted(results_imdb, key=lambda x: x.rating, reverse=True)

        q = ZdbQuery(Files, session=db.session)
        q = q.filter(Files.meta_imdb_id.in_(ids))
        q = q.filter(Files.file_size >= 134217728)
        results_local = q.all()
        # @TODO: migrate `meta_info` to JSONB so we get the #> operator
        # with that we can DISTINCT on nested json key 'title'
        # e.g: SELECT DISTINCT ON (files.meta_info#>'{ptn, title}')
        # to prevent from returning duplicates in popcorn view.
        # for now, lets just do this:
        _names = []
        _rtn = []
        for result in results_local:
            result.get_meta_imdb()
            if result.meta_imdb.title not in _names:
                _rtn.append(result)
                _names.append(result.meta_imdb.title)
        _rtn = sorted(_rtn, key=lambda x: x.meta_imdb.title, reverse=True)

        return {
            "local": _rtn,
            "imdb": results_imdb
        }

    @staticmethod
    def get_director_directed(director):
        """Returns a list of movies given a director"""

        q = ZdbQuery(MetaImdb, session=db.session)
        q = q.filter(MetaImdb.director.like(director))
        results_imdb = q.all()
        if not results_imdb:
            return {
                "local": [],
                "imdb": []
            }

        ids = [z.id for z in results_imdb]
        results_imdb = sorted(results_imdb, key=lambda x: x.rating, reverse=True)

        q = ZdbQuery(Files, session=db.session)
        q = q.filter(Files.meta_imdb_id.in_(ids))
        q = q.filter(Files.file_size >= 134217728)

        results_local = q.all()
        # @TODO: migrate `meta_info` to JSONB so we get the #> operator
        # with that we can DISTINCT on nested json key 'title'
        # e.g: SELECT DISTINCT ON (files.meta_info#>'{ptn, title}')
        # to prevent from returning duplicates in popcorn view.
        # for now, lets just do this:
        _names = []
        _rtn = []
        for result in results_local:
            result.get_meta_imdb()
            if result.meta_imdb.title not in _names:
                _rtn.append(result)
                _names.append(result.meta_imdb.title)
        _rtn = sorted(_rtn, key=lambda x: x.meta_imdb.title, reverse=True)
        return {
            "local": _rtn,
            "imdb": results_imdb
        }

    @staticmethod
    def search(actors: List = None, genres: List = None, min_rating: int = None,
               director: str = None, year: int = None,
               offset: int = None, limit: int = 12):
        if actors:
            if not isinstance(actors, list):
                raise SearchException("actors must be list")
        if genres:
            if not isinstance(genres, list):
                raise SearchException("genres must be list")
        if min_rating:
            if not isinstance(min_rating, (int, float)):
                raise SearchException("min_rating must be int")
            if not min_rating > 0 or min_rating > 100:
                raise SearchException("min_rating must be between 1-100")
            if min_rating <= 10:
                min_rating = int(min_rating * 10)
        if director and not isinstance(director, str):
            raise SearchException("director must be str")
        if year:
            if not isinstance(year, int):
                raise Exception("year must be int")
        if offset:
            if not isinstance(offset, int):
                raise Exception("offset must be int")
        if limit:
            if not isinstance(limit, int):
                raise Exception("limit must be int")

        if actors or genres or min_rating or director or year:
            q = ZdbQuery(MetaImdb, session=db.session)
        else:
            q = db.session.query(Files)
            q = q.filter(Files.meta_imdb_id != None)
            q = q.filter(Files.file_size >= 134217728)
            q = q.limit(12)
            if offset:
                q = q.offset(offset)
            results = q.all()
            for result in results:
                result.get_meta_imdb()
            return results

        if actors:
            q = q.filter(MetaImdb.actors.in_(actors))

        if genres:
            q = q.filter(MetaImdb.genres.in_(genres))

        if min_rating:
            q = q.filter(MetaImdb.rating >= min_rating)

        if year:
            q = q.filter(MetaImdb.year == year)

        if director:
            q = q.filter(MetaImdb.director == director)

        results = q.all()
        if not results:
            return []

        ids = list(set([z.id for z in results]))

        q = ZdbQuery(Files, session=db.session)
        q = q.filter(Files.meta_imdb_id.in_(ids))
        q = q.filter(Files.file_size >= 134217728)
        q = q.limit(45)
        results = q.all()

        # @TODO: migrate `meta_info` to JSONB so we get the #> operator
        # with that we can DISTINCT on nested json key 'title'
        # e.g: SELECT DISTINCT ON (files.meta_info#>'{ptn, title}')
        # to prevent from returning duplicates in popcorn view.
        # for now, lets just do this:
        _names = []
        _rtn = []
        for result in results:
            result.get_meta_imdb()
            if result.meta_imdb.title not in _names:
                _rtn.append(result)
                _names.append(result.meta_imdb.title)
        return _rtn
