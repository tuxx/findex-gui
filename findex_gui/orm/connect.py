import random
import psycopg2
import logging
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text
from sqlalchemy import pool

import settings
from findex_gui.orm.models import BASE
from findex_common.exceptions import DatabaseException, ElasticSearchException


class Database(object):
    def __init__(self, hosts, port, name, user, passwd):
        """
        Connects to the Postgres database.
        :param hosts: list of strings, to be used in the connection pool
        :param port: int
        :param name: database name
        :param user: database user
        :param passwd: database password
        """
        self.engine = None
        self.session = None

        self.hosts = hosts
        self.port = port
        self.name = name
        self.user = user
        self.passwd = passwd

        self.pool = pool.QueuePool(creator=self._getconn,
                                   max_overflow=1,
                                   pool_size=300,
                                   echo=settings.app_debug)

    def connect(self):
        self.engine = create_engine('postgresql+psycopg2://',
                                    pool=self.pool,
                                    echo=settings.app_debug)
        self.session = scoped_session(sessionmaker(autocommit=True,
                                                   autoflush=True,
                                                   expire_on_commit=True,
                                                   bind=self.engine))
        BASE.query = self.session.query_property()

    def bootstrap(self):
        # check if es can be reached
        # if settings.es_enabled:
        #     try:
        #         r = requests.get(settings.es_host, verify=False, timeout=1)
        #         r.raise_for_status()
        #     except:
        #         raise ElasticSearchException("ElasticSearch is down? (%s)" % settings.es_host)

        # check necessary postgres extensions
        self.create_extension(
            extension="pg_trgm",
            msg_on_activate_error="Postgres extension \"pg_trgm\" installed but "
                                  "could not be enabled, "
                                  "possibly missing administrator rights to enable "
                                  "pg_trgm: `CREATE EXTENSION pg_trgm;`")
        if settings.es_enabled:
            self.create_extension(
                extension="zombodb",
                msg_on_activate_error="Postgres extension \"zombodb\" installed but "
                                      "could not be enabled.")

        # create the tables, types and indexes
        import findex_gui.orm.events
        BASE.metadata.create_all(bind=self.engine)

        if settings.es_enabled:
            # check required types for es
            if not self.check_type(type_name="type_files"):
                raise DatabaseException("Postgres type `type files` not found. "
                                        "Try the following SQL to rebuild the table:\n"
                                        "\tDROP TYPE type_files CASCADE;\n"
                                        "\tDROP TABLE files;\n")
            # check if the zombodb index is present
            if not self.check_index(table_name="files", index="idx_zdb_files"):
                raise DatabaseException("Postgres index `idx_zdb_files` not found "
                                        "while settings.es_enabled was ``True``.\n"
                                        "Try the following SQL to rebuild the table:\n"
                                        "\tDROP TYPE type_files CASCADE;\n"
                                        "\tDROP TABLE files;\n")
        else:
            if self.check_index(table_name="files", index="idx_zdb_files"):
                raise DatabaseException("Please remove the index `idx_zdb_files` before "
                                        "using findex without ES enabled:\n"
                                        "\tDROP INDEX idx_zdb_files\n"
                                        "\tcurl -XDELETE %sdb.schema.table.index" % settings.es_host)

        from findex_gui.controllers.user.user import UserController
        from findex_gui.controllers.user.roles import default_anon_roles
        from findex_gui.controllers.resources.resources import ResourceController
        from findex_gui.controllers.tasks.tasks import TaskController

        # add some default users, groups and tasks to the database
        if not UserController.user_view(username="root"):
            UserController.user_add(
                username="root",
                password=settings.auth_default_root_pw,
                removeable=False,
                admin=True,
                skip_authorization=True)

        if not UserController.user_view(username="anon"):
            UserController.user_add(
                username="anon",
                password=settings.auth_default_anon_pw,
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

    def check_index(self, table_name: str, index: str):
        """
        Checks for the presence of a given Postgres index
        :param table_name: name of the table
        :param index: name of the index
        :return: A :class:`sqlalchemy.engine.result.RowProxy` instance.
        """
        sql = """
        SELECT schemaname, tablename, indexname, indexdef FROM pg_indexes
        WHERE tablename = :table_name AND indexname = :index;
        """
        return self.session.execute(text(sql), params={"table_name": table_name, "index": index}).fetchone()

    def check_type(self, type_name: str):
        """
        Checks for the presence of a given Postgres type
        :param type_name: name of the type
        :return: A :class:`sqlalchemy.engine.result.RowProxy` instance if found.
        """
        sql = """
        SELECT
          n.nspname AS schema,
          t.typname AS type
        FROM pg_type t
          LEFT JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
        WHERE (t.typrelid = 0 OR (SELECT c.relkind = 'c'
                                  FROM pg_catalog.pg_class c
                                  WHERE c.oid = t.typrelid))
              AND NOT EXISTS(SELECT 1
                             FROM pg_catalog.pg_type el
                             WHERE el.oid = t.typelem AND el.typarray = t.oid)
              AND n.nspname NOT IN ('pg_catalog', 'information_schema')
              AND t.typname=:type_name;
        """
        return self.session.execute(text(sql), params={"type_name": type_name}).fetchone()

    def check_extension(self, extension: str):
        """
        Checks for the presence of a given Postgres extension
        :param extension: name of the extension
        :return: A :class:`sqlalchemy.engine.result.RowProxy` instance if found.
        """
        sql = """
        SELECT name,installed_version FROM pg_available_extensions WHERE name=:extension
        """
        return self.session.execute(text(sql), params={"extension": extension}).fetchone()

    def create_extension(self, extension: str, msg_on_activate_error: str):
        """
        Tries to activate a Postgres extension
        :param extension: name of the Postgres extension
        :param msg_on_activate_error: exception message to raise when the
        extension could not be activated
        :return:
        """
        extension = self.check_extension(extension)
        if not extension:
            raise DatabaseException("Postgres extension \"%s\" not installed" % extension)

        if not extension.installed_version:
            self.session.execute("CREATE EXTENSION :extension", params={"extension": extension})
            self.session.commit()
            self.session.flush()

            extension = self.check_extension(extension)
            if not extension:
                raise DatabaseException("Postgres extension \"%s\" not installed" % extension)
            if not extension.installed_version:
                raise DatabaseException(msg_on_activate_error)
            else:
                logging.debug("Enabled database extension \"%s\"" % extension)

    def _getconn(self):
        random.shuffle(self.hosts)
        for host in self.hosts:
            try:
                return psycopg2.connect(host=host, user=self.user,
                                        dbname=self.name, password=self.passwd,
                                        port=self.port)
            except psycopg2.OperationalError as e:
                print('Failed to connect to %s: %s' % (host, e))
        raise psycopg2.OperationalError("Ran out of database servers - exiting")
