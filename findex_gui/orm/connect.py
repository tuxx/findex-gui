import random
import psycopg2
import sqlalchemy
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import pool

from findex_gui.orm.models import base, Options, Roles, UserGroup, User
from findex_common.exceptions import DatabaseException

# https://github.com/Mikulas/pg-es-fdw


class Orm(object):
    def __init__(self, app):
        self.app = app
        self.engine = None
        self.session = None

        self._db_hosts = app.config['DB_HOSTS']
        self._db_port = app.config['DB_PORT']
        self._db_database = app.config['DB_DB']
        self._db_user = app.config['DB_USER']
        self._db_pass = app.config['DB_PASS']

    def init(self):
        base.metadata.create_all(bind=self.engine)
        self._init_users()

    def _init_users(self):
        from findex_gui.controllers.user.user import UserController
        UserController.user_add(username="root", password="root", removeable=False, admin=True, skip_authorization=True)
        UserController.user_add(username="anon", password="anonymous", removeable=False, skip_authorization=True)
        UserController.user_view(1)

class Postgres(Orm):
    def __init__(self, app):
        super(Postgres, self).__init__(app)

        if not isinstance(self._db_hosts, list):
            self._db_hosts = [self._db_hosts]
        else:
            if ',' in self._db_hosts:
                self._db_hosts = self._db_hosts.split(',')

        self.pool = pool.QueuePool(
            creator=self._getconn, max_overflow=1, pool_size=20, echo=True)

    def connect(self):
        self.engine = create_engine('postgresql+psycopg2://', pool=self.pool, echo=True)
        self.session = scoped_session(sessionmaker(autocommit=False,
                                                   autoflush=True,
                                                   bind=self.engine))

        base.query = self.session.query_property()
        pg_trgm = self.session.execute("""
            SELECT name,installed_version FROM pg_available_extensions WHERE name='pg_trgm';
        """).fetchall()

        if not pg_trgm:
            raise DatabaseException("Postgres extension pg_trgm not installed; "
                                    "https://packages.debian.org/jessie/arm64/postgresql-contrib-9.4/filelist")
        else:
            if not pg_trgm[0].installed_version:
                self.session.execute("CREATE EXTENSION pg_trgm;")
                self.session.commit()
                self.session.flush()

                pg_trgm = self.session.execute("""
                SELECT * FROM pg_available_extensions WHERE name ='pg_trgm';
                """).fetchall()

                if not pg_trgm[0].installed_version:
                    raise DatabaseException("Postgres extension pg_trgm installed but "
                                            "could not be activated in the current database, "
                                            "probably missing administrator rights to enable "
                                            "pg_trgm: `CREATE EXTENSION pg_trgm;`")
                else:
                    logging.debug("Enabled database extension \"pg_trgm\"")
        self.init()

    def _getconn(self):
        random.shuffle(self._db_hosts)
        for host in self._db_hosts:
            try:
                return psycopg2.connect(host=host, user=self._db_user,
                                        dbname=self._db_database, password=self._db_pass,
                                        port=self._db_port)
            except psycopg2.OperationalError as e:
                print 'Failed to connect to %s: %s' % (host, e)
        raise psycopg2.OperationalError("Ran out of database servers - exiting")
