import random
import psycopg2

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import pool

from findex_gui.orm.models import base, Options

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

        options = {}
        for option in Options.query.all():
            options[option.key] = option.val


class Postgres(Orm):
    def __init__(self, app):
        super(Postgres, self).__init__(app)

        if not isinstance(self._db_hosts, list):
            self._db_hosts = [self._db_hosts]
        else:
            if ',' in self._db_hosts: self._db_hosts = self._db_hosts.split(',')

        self.pool = pool.QueuePool(self._getconn, max_overflow=1, pool_size=20, echo=True)

    def connect(self):
        self.engine = create_engine('postgresql+psycopg2://', pool=self.pool, echo=True)
        self.session = scoped_session(sessionmaker(autocommit=False,
                                                   autoflush=False,
                                                   bind=self.engine))

        base.query = self.session.query_property()
        self.init()

    def _getconn(self):
        random.shuffle(self._db_hosts)
        for host in self._db_hosts:
            try:
                return psycopg2.connect(host=host, user=self._db_user, dbname=self._db_database, password=self._db_pass)
            except psycopg2.OperationalError as e:
                print 'Failed to connect to %s: %s' % (host, e)

        raise psycopg2.OperationalError("Ran out of database servers - exiting")
