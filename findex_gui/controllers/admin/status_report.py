import os
import sys
from collections import OrderedDict

from sqlalchemy.sql import text

from findex_gui.web import db
from findex_gui.bin.config import config
from findex_gui.bin.misc import version, cwd
from findex_gui.controllers.amqp.amqp import AmqpController


class AdminStatusReport:
    @staticmethod
    def status():
        """return big ass dict with as much info as possible about this findex instance"""
        data = OrderedDict()
        data["findex"] = OrderedDict([
            ("version", _item(cls="info", data=version)),
            ("debug mode", _item(str(config("findex:findex:debug")))),
            ("config_location", _item(cwd())),
            ("application_root", _item(config("findex:findex:application_root"))),
            ("async mode", _item(config("findex:findex:async"))),
            ("No. Findex Users", AdminStatusReport.findex_get_nousers())
        ])

        data["system"] = OrderedDict([
            ("Kernel", _item(os.popen("uname -r").read())),
            ("Memory", _item(AdminStatusReport.system_get_memory())),
            ("No. CPUs", AdminStatusReport.system_get_nocpus()),
            ("Python Version", AdminStatusReport.system_python_version())
        ])

        data["database"] = OrderedDict([
            ("encoding", AdminStatusReport.raw_query("SHOW SERVER_ENCODING", cls="info")),
            ("connection string (RFC-1738)", _item(config("findex:database:connection"))),
            ("database system version", AdminStatusReport.raw_query("SELECT version();")),
            ("size on disk", AdminStatusReport.database_get_size()),
        ])

        _amqp = AdminStatusReport.amqp_get_credentials()
        data["rabbitmq"] = OrderedDict([
            ("username", _amqp["username"]),
            ("host", _amqp["host"]),
            ("vhost", _amqp["vhost"]),
            ("queue_name", _amqp["queue_name"])
        ])

        from pip.operations import freeze
        _packages = freeze.freeze()
        packages = []
        for _package in _packages:
            _package = _package.strip()
            if not _package:
                continue
            if _package.startswith("-e"):
                packages.append(("-e", _item(_package[3:])))
            else:
                _pack, _ver = _package.split("==", 1)
                packages.append((_pack, _item(_ver)))

        data["pip"] = OrderedDict(packages)
        return data

    @staticmethod
    def findex_get_nousers():
        from findex_gui.orm.models import User
        try:
            return _item("%d user(s)" % len(db.session.query(User).all()), cls="ok")
        except:
            db.session.rollback()
            return _item("error fetching users", cls="error")

    @staticmethod
    def system_python_version():
        return _item(sys.version)

    @staticmethod
    def system_get_nocpus():
        return _item(os.popen("cat /proc/cpuinfo | grep \"model name\" | wc -l").read())

    @staticmethod
    def system_get_memory():
        meminfo = dict((i.split()[0].rstrip(':'), int(i.split()[1])) for i in open('/proc/meminfo').readlines())
        mem_kib = meminfo['MemTotal']
        return "%d Megabyte" % (mem_kib/1000)

    @staticmethod
    def database_get_size():
        db_dsn = config("findex:database:connection")
        db_info = db.parse_connection_string(db_dsn)
        sql = """
        SELECT
            pg_size_pretty(pg_database_size(pg_database.datname)) AS size
        FROM pg_database WHERE datname=:db_name;
        """
        res = AdminStatusReport.raw_query(sql, {"db_name": db_info["name"]})
        if res.cls != "ok":
            return res

        data_dir = AdminStatusReport.raw_query("""show data_directory;""")
        if data_dir.cls != "ok":
            res.data += " (error fetching data_dir)"
            return res

        res.data += " @ %s" % data_dir.data
        return res

    @staticmethod
    def raw_query(sql: str, params: dict = None, cls: str = "ok"):
        try:
            res = db.session.execute(text(sql), params=params).fetchone()
            if not res or not res.items():
                return res
            if isinstance(res.values(), (tuple, list)):
                res = ",".join(res.values())
            return _item(data=res, cls=cls)
        except Exception as ex:
            db.session.rollback()
            return _item(cls="error", data=str(ex))

    @staticmethod
    def amqp_get_credentials():
        creds = AmqpController.get_credentials()
        if not creds:
            creds = {}
        _rtn = OrderedDict()

        for expect in ["username", "host", "vhost", "queue_name"]:
            if expect not in creds:
                _rtn[expect] = _item(cls="error", data="%s empty" % expect)
            else:
                _rtn[expect] = _item(creds[expect])
        return _rtn

class _item:
    def __init__(self, data: str = None, cls: str = "ok"):
        """
        :param cls: ok, info, warning
        :param data:
        """
        self.cls = cls
        self.data = data
