import os
import sys
from collections import OrderedDict

import dsnparse
from sqlalchemy.sql import text

from findex_gui.web import db, app
from findex_gui.bin.config import config
from findex_gui.bin.misc import version, cwd
from findex_gui.bin.utils import get_pip_freeze
from findex_gui.controllers.tasks.crawler import Crawler
from findex_gui.bin.utils import is_gevent_monkey_patched
from findex_gui.controllers.admin.scheduler.cron import CronController
# from findex_gui.controllers.amqp.amqp import AmqpController

SECTIONS = ["findex", "database", "system", "pip"]


class AdminStatusController(object):
    @staticmethod
    def overview():
        results = OrderedDict()
        for func in SECTIONS:
            result = getattr(AdminStatusController, func)()
            results[func] = {
                "data": result,
                "has_errors": len(AdminStatusController._check_errs(result, _errs=[])[0])
            }
        return results

    @staticmethod
    def _check_errs(inp, _errs=[], _checked=0):
        if isinstance(inp, list):
            return AdminStatusController._check_errs(inp=inp, _errs=_errs, _checked=_checked)
        if not isinstance(inp, dict):
            return _errs

        for k, v in inp.items():
            _checked += 1
            if v is None:
                continue

            if v.cls.lower() not in ["ok", "info"]:
                _errs.append(v)

        return _errs, _checked

    @staticmethod
    def has_errors(section=None):
        """
        Returns the number of items checked,
        and the numbers of errors returned
        during the various status checks
        :param section: specific section to check
        :return: int
        """
        errs = []
        if section:
            sections = [section]
        else:
            sections = SECTIONS

        checked = 0

        for func in sections:
            result = getattr(AdminStatusController, func)()
            errors, _checked = AdminStatusController._check_errs(inp=result, _errs=[])
            for error in errors:
                errs.append(error)
            checked += _checked
        return errs, checked

    @staticmethod
    def findex():
        rtn = OrderedDict()
        rtn["Version"] = _item(cls="info", data=version)
        rtn["Debug"] = _item(str(config("findex:findex:debug")))
        rtn["Config Location"] = _item(cwd())
        rtn["Application Root"] = _item(config("findex:findex:application_root"))

        is_async = "True" if is_gevent_monkey_patched() else "False"
        rtn["Async mode (Gevent monkey patch)"] = _item(is_async)
        rtn["No. Findex Users"] = FindexStatus.findex_get_nousers()
        try:
            Crawler.can_crawl()
            can_crawl = _item("Available", cls="ok")
        except Exception as ex:
            can_crawl = _item(str(ex), cls="error")
        rtn["'DIRECT' crawl mode"] = can_crawl

        has_cron = CronController.has_cronjob()
        has_cron_err = "Not set, please activate it (Scheduler->Overview)"
        has_cron = has_cron_err if not has_cron else "Set"
        rtn["Scheduler cronjob"] = _item(has_cron, cls="info" if has_cron == "Set" else "error")
        return rtn

    @staticmethod
    def database():
        rtn = OrderedDict()

        dsn = config("findex:database:connection")
        rtn["dsn (RFC-1738)"] = _item(data=dsn, cls="info")

        encoding = DatabaseStatus.raw_query("SHOW SERVER_ENCODING", cls="ok")
        if "UTF8" not in encoding.data:
            encoding.cls = "warning"
        rtn["encoding"] = encoding

        dsn_parsed = dsnparse.parse(dsn)
        dsn_blob = {
            "user": dsn_parsed.username,
            "pass": dsn_parsed.password,
            "host": dsn_parsed.host,
            "port": 5432 if not isinstance(dsn_parsed.port, int) else dsn_parsed.port,
            "db": dsn_parsed.paths[0]}

        for k, v in dsn_blob.items():
            rtn["db_%s" % k] = _item(data=v, cls="ok")

        rtn["Size on Disk"] = DatabaseStatus.get_size()
        return rtn

    @staticmethod
    def system():
        return OrderedDict([
            ("Kernel", _item(os.popen("uname -r").read())),
            ("Memory", _item(SystemStatus.memory())),
            ("No. CPUs", SystemStatus.nocpus()),
            ("Python Version", SystemStatus.pyversion())
        ])

    @staticmethod
    def pip():
        # @TODO: compare with setup.py/requirements.txt
        rtn = OrderedDict()
        freezed_date, freezed_packages = get_pip_freeze()
        rtn["updated: %s" % freezed_date.strftime("%Y-%m-%d %H:%M")] = None

        for f in freezed_packages:
            rtn[f[0]] = _item(f[1], cls="ok")

        OrderedDict([(f[0], _item(f[1])) for f in freezed_packages])
        return rtn


class AmqpStatus(AdminStatusController):
    def __init__(self):
        super(AmqpStatus, self).__init__()

    def info(self):
        from findex_gui.orm.models import Mq

        rtn = []

        for mq in db.session.query(Mq).all():
            _rtn = OrderedDict()

            for column_name in ["name", "host", "port", "vhost", "queue",
                                "broker_type" "auth_user", "auth_pass"]:
                _rtn[column_name.capitalize()] = _item(data=getattr(mq, column_name), cls="ok")
            rtn.append(_rtn)
        return rtn

class FindexStatus(AdminStatusController):
    def __init__(self):
        super(FindexStatus, self).__init__()

    @staticmethod
    def findex_get_nousers():
        from findex_gui.orm.models import User
        try:
            return _item("%d user(s)" % len(db.session.query(User).all()), cls="ok")
        except:
            db.session.rollback()
            return _item("error fetching users", cls="error")


class SystemStatus(AdminStatusController):
    def __init__(self):
        super(SystemStatus, self).__init__()

    @staticmethod
    def pyversion():
        return _item(sys.version)

    @staticmethod
    def nocpus():
        return _item(os.popen("cat /proc/cpuinfo | grep \"model name\" | wc -l").read())

    @staticmethod
    def memory():
        meminfo = dict((i.split()[0].rstrip(':'), int(i.split()[1])) for i in open('/proc/meminfo').readlines())
        mem_kib = meminfo['MemTotal']
        return "%d Megabyte" % (mem_kib/1000)


class DatabaseStatus(AdminStatusController):
    def __init__(self):
        super(DatabaseStatus, self).__init__()

    @staticmethod
    def get_size():
        dsn = dsnparse.parse(config("findex:database:connection"))
        db_name = dsn.paths[0]
        sql = """
        SELECT
            pg_size_pretty(pg_database_size(pg_database.datname)) AS size
        FROM pg_database WHERE datname=:db_name;
        """
        res = DatabaseStatus.raw_query(sql, {"db_name": db_name})
        if res.cls != "ok":
            return res

        data_dir = DatabaseStatus.raw_query("""show data_directory;""")
        if data_dir.cls != "ok":
            res.data += " (error fetching data_dir)"
            return res
        else:
            res.cls = "info"

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


class _item:
    def __init__(self, data: str = None, cls: str = "ok"):
        """
        :param cls: ok, info, warning
        :param data:
        """
        self.cls = cls
        self.data = data