from gevent import monkey
monkey.patch_all()

import psycogreen.gevent
psycogreen.gevent.patch_psycopg()


import sqlalchemy as sql
from sqlalchemy import or_
import sqlalchemy.pool as pool
import bottle_sqlalchemy as sqlalchemy
from sqlalchemy import create_engine, Column, Sequence, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import INET
import random
import psycogreen
import psycopg2


Base = declarative_base()


class Postgres():
    def __init__(self, cfg, app=None):
        self.cfg = cfg

        self._db_hosts = self.cfg['database']['host']
        self._db_port = self.cfg['database']['port']
        self._db_database = self.cfg['database']['database']
        self._db_user = self.cfg['database']['username']
        self._db_pass = self.cfg['database']['password']

        if not isinstance(self._db_hosts, list):
            self._db_hosts = [self._db_hosts]
        else:
            if ',' in self._db_hosts: self._db_hosts = self._db_hosts.split(',')

        self.pool = pool.QueuePool(self._getconn, max_overflow=1, pool_size=2, echo=self.cfg['database']['debug'])
        self.engine = create_engine('postgresql+psycopg2://', pool=self.pool, echo=self.cfg['database']['debug'])

        self.plugin = sqlalchemy.Plugin(
            self.engine,
            Base.metadata,
            keyword='db',
            create=True,
            commit=False,
            use_kwargs=False
        )

        if app:
            Base.metadata.create_all(self.engine)
            app.install(self.plugin)

    def _getconn(self):
        random.shuffle(self._db_hosts)
        for host in self._db_hosts:
            try:
                return psycopg2.connect(host=host, user=self._db_user, dbname=self._db_database, password=self._db_pass)
            except psycopg2.OperationalError as e:
                print 'Failed to connect to %s: %s' % (host, e)

        raise psycopg2.OperationalError("Ran out of database servers - exiting")


class Files(Base):
    __tablename__ = 'files'
 
    id = Column(sql.Integer, primary_key=True)

    resource_id = Column(sql.Integer())

    file_name = Column(sql.String())
    file_path = Column(sql.String())
    file_ext = Column(sql.String(8))
    file_format = Column(sql.Integer())
    file_isdir = Column(sql.Boolean())
    file_size = Column(sql.BigInteger())

    file_modified = Column(sql.DateTime())

    file_perm = Column(sql.Integer())

    searchable = Column(sql.String(23))

    def __init__(self, file_name, file_path, file_ext, file_format, file_isdir, file_modified, file_perm, searchable, file_size, resource_id, img_icon=None):
        self.resource_id = resource_id
        self.file_name = file_name
        self.file_path = file_path
        self.file_ext = file_ext
        self.file_format = file_format
        self.file_size = file_size
        self.file_isdir = file_isdir
        self.file_modified = file_modified
        self.file_perm = file_perm
        self.searchable = searchable
        self.img_icon = None

    # regular indexes
    ix_file_ext = Index('ix_file_ext', file_ext)
    ix_file_size = Index('ix_file_size', file_size)

    # multi column indexes
    ix_host_id_file_path = Index('ix_resource_id_file_path', resource_id, file_path)
    ix_file_format_searchable = Index('ix_file_format_searchable', file_format, searchable)

    # partial text search LIKE 'needle%'
    ix_file_searchable_text = Index('ix_file_searchable_text', searchable, postgresql_ops={
        'searchable': 'text_pattern_ops'
    })

    # full text search LIKE '%needle%'
    ix_file_searchable_gin = Index('ix_file_searchable_gin', searchable, postgresql_using='gin', postgresql_ops={
        'searchable': 'gin_trgm_ops'
    })


class Crawlers(Base):
    __tablename__ = 'crawlers'

    id = Column(sql.Integer, primary_key=True)
    hostname = Column(sql.String(), nullable=False)
    crawler_name = Column(sql.String(), nullable=False)

    jsonrpc_bind_host = Column(INET())
    jsonrpc_bind_port = Column(sql.Integer())

    jsonrpc = Column(sql.Boolean())
    amqp = Column(sql.Boolean())
    amqp_name = Column(sql.String(128))

    heartbeat = Column(sql.TIMESTAMP())


class Resources(Base):
    __tablename__ = 'resources'

    id = Column(sql.Integer, primary_key=True)

    name = Column(sql.String(), nullable=False)
    description = Column(sql.String())

    address = Column(INET())
    display_url = Column(sql.String(), nullable=False)

    date_added = Column(sql.DateTime())
    date_crawl_start = Column(sql.DateTime())
    date_crawl_end = Column(sql.DateTime())

    file_count = Column(sql.Integer())
    protocol = Column(sql.Integer(), nullable=False)

    # regular indexes
    ix_address = Index('ix_address', address)

    def __init__(self, address, display_url, date_added, date_crawl_start, date_crawl_end, file_count, protocol, description):
        self.address = address
        self.display_url = display_url
        self.date_added = date_added
        self.date_crawl_start = date_crawl_start
        self.date_crawl_end = date_crawl_end
        self.file_count = file_count
        self.protocol = protocol
        self.description = description


class Options(Base):
    __tablename__ = 'options'

    id = Column(sql.Integer, primary_key=True)

    key = Column(sql.String())
    val = Column(sql.String())

    def __init__(self, key, val):
        self.key = key
        self.val = val