import json
import urllib
from sqlalchemy import and_
from bottle import response, jinja2_template

from db.orm import Files, Hosts
from controllers.helpers import data_strap

from findex_common.utils import ArgValidate
from findex_common.bytes2human import bytes2human


class Documentation():
    def __init__(self, cfg, db):
        self.cfg = cfg
        self.db = db
        self.arg_validate = ArgValidate()

    @data_strap
    def docu(self, env):
        return jinja2_template('main/documentation', env=env)
