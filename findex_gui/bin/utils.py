from datetime import datetime, date

import flask
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy_zdb import ZdbColumn
from sqlalchemy_json import MutableJson

from flask import url_for as _url_for
from flask import redirect as _redirect
from flask.json import JSONEncoder

def dirty_url_for():
    """dirty flask.url_for() monkey patch."""
    from findex_gui.web import app
    flask.url_for = lambda *args, **kwargs: "%s%s" % (app.config["APPLICATION_ROOT"][:-1], _url_for(*args, **kwargs))

def redirect(*args, **kwargs):
    __redirect = _redirect(*args, **kwargs)
    __redirect.autocorrect_location_header = False
    return __redirect
flask.redirect = redirect


class ApiJsonEncoder(JSONEncoder):
    """Custom JSON encoder for flask.jsonify that returns ISO 8601
    strings which can be parsed in javascript with Date.parse()"""
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


class Extended(object):
    def get(self, column, default=None):
        if hasattr(self, column):
            val = getattr(self, column)
            return val if val else default
        return default

    def get_json(self, _depth=0):
        if _depth > 1:
            return

        json = {}
        for k, v in self.__class__.__dict__.items():
            if k.startswith("_"):
                continue
            if not issubclass(v.__class__, (property, InstrumentedAttribute)):
                continue

            if isinstance(v, InstrumentedAttribute):
                if "json_exclude" in v.info and v.info["json_exclude"]:
                    value = "***"
                else:
                    value = getattr(self, k)
            else:
                value = getattr(self, k)

            from findex_gui.orm.models import BASE
            if issubclass(value.__class__, BASE):
                value = value.get_json(_depth + 1)
            if isinstance(value, list):
                _value = []
                for _v in value:
                    if hasattr(_v, "get_json"):
                        _value.append(_v.get_json(_depth + 1))
                    else:
                        _value.append(str(_v))
                json[k] = _value
            else:
                json[k] = value
        return json

    @classmethod
    def get_columns(cls, zombodb_only=False):
        """
        Returns the columns for a given sqlalchemy model
        :param zombodb_only: only return columns marked for zombodb
        :return: list of columns
        """
        columns = list(cls.__table__.columns)
        if zombodb_only:
            columns = [c for c in columns if isinstance(c, ZdbColumn)]
        return columns

    @classmethod
    def get_columns_as_ddl(cls, zombodb_only=False):
        """
        Returns the column(s) DDL for a given sqlalchemy model
        :param zombodb_only: only return columns marked for zombodb
        :return:
        """
        rtn = []
        for column in cls.get_columns(zombodb_only=zombodb_only):
            if isinstance(column.type, MutableJson): column_type = "JSON"
            else: column_type = column.type
            rtn.append("%s %s" % (column.name, column_type))
        return ",\n\t".join(rtn)

    def __repr__(self):
        return "%s" % self.__class__


def pip_freeze():
    from pip.operations import freeze
    _packages = freeze.freeze()
    packages = []
    for _package in _packages:
        _package = _package.strip()
        if not _package:
            continue
        if _package.startswith("-e"):
            packages.append(["-e", _package[3:]])
        else:
            _pack, _ver = _package.split("==", 1)
            packages.append([_pack, _ver])
    return packages

def get_pip_freeze():
    from findex_gui.web import app
    if not app.config['PIP_FREEZE']:
        app.config['PIP_FREEZE'] = (datetime.now(), pip_freeze())

    if (datetime.now() - app.config['PIP_FREEZE'][0]).days >= 2:
        # refresh the pip freeze output every 2 days
        app.config['PIP_FREEZE'] = (datetime.now(), pip_freeze())
    return app.config["PIP_FREEZE"]
