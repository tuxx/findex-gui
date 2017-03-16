import random
import psycopg2
import sqlalchemy
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import pool

import settings
from findex_gui.orm.models import base, Options, Roles, UserGroup, User
from findex_common.exceptions import DatabaseException

# https://github.com/Mikulas/pg-es-fdw


class Orm(object):
    def __init__(self, app, **kwargs):
        self.app = app
        self.engine = None
        self.session = None

        if "db_hosts" in kwargs:
            self._db_hosts = kwargs["db_hosts"]
        else:
            self._db_hosts = app.config['DB_HOSTS']
        if "db_port" in kwargs:
            self._db_port = kwargs["db_port"]
        else:
            self._db_port = app.config['DB_PORT']
        if "db_db" in kwargs:
            self._db_database = kwargs["db_db"]
        else:
            self._db_database = app.config['DB_DB']
        if "db_user" in kwargs:
            self._db_user = kwargs["db_user"]
        else:
            self._db_user = app.config['DB_USER']
        if "db_pass" in kwargs:
            self._db_pass = kwargs["db_pass"]
        else:
            self._db_pass = app.config['DB_PASS']

    def init(self):
        base.metadata.create_all(bind=self.engine)
        Orm.fixtures()

    @staticmethod
    def fixtures():
        from findex_gui.controllers.user.user import UserController
        from findex_gui.controllers.user.roles import default_anon_roles
        from findex_gui.controllers.resources.resources import ResourceController
        from findex_gui.controllers.tasks.tasks import TaskController

        # add some default users, groups and tasks to the database
        if not UserController.user_view(username="root"):
            UserController.user_add(
                username="root",
                password=settings.default_root_pw,
                removeable=False,
                admin=True,
                skip_authorization=True)

        if not UserController.user_view(username="anon"):
            UserController.user_add(
                username="anon",
                password=settings.default_anon_pw,
                privileges=default_anon_roles,
                removeable=False,
                skip_authorization=True)

        if not ResourceController.get_resource_group(name="Default"):
            ResourceController.add_resource_group(
                name="Default",
                description="Default group",
                removable=False,
                skip_authorization=True,
                log_error=False,
                ignore_constraint_conflict=True)

        def_task = TaskController.get_task(name="Default")
        if not def_task:
            def_task = TaskController.add_task(
                name="Default",
                owner_id=1,
                skip_authorization=True,
                log_error=False,
                ignore_constraint_conflict=True)

        if not def_task.groups:
            TaskController.assign_resource_group(
                task_id=1,
                resourcegroup_id=1,
                skip_authorization=True,
                log_error=False,
                ignore_constraint_conflict=True)


class Postgres(Orm):
    def __init__(self, app, **kwargs):
        super(Postgres, self).__init__(app, **kwargs)

        if not isinstance(self._db_hosts, list):
            self._db_hosts = [self._db_hosts]
        else:
            if ',' in self._db_hosts:
                self._db_hosts = self._db_hosts.split(',')

        self.pool = pool.QueuePool(
            creator=self._getconn, max_overflow=1, pool_size=300, echo=False)

    def connect(self, init=True):
        self.engine = create_engine('postgresql+psycopg2://', pool=self.pool, echo=False)
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
        if init:
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
