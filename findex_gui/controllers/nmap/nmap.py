import os
from findex_gui.web import db
from findex_gui.orm.models import NmapRule
from findex_gui.controllers.user.roles import role_req


class NmapController:
    @staticmethod
    @role_req("ADMIN")
    def get(uid: str = None, limit: int = None, offset: int = None):
        q = db.session.query(NmapRule)
        if uid:
            return q.filter(NmapRule.id == uid).first()
        if isinstance(limit, int):
            q = q.limit(limit)
        if isinstance(offset, int):
            q = q.offset(offset)

        return q.all()

    @staticmethod
    @role_req("ADMIN")
    def add(cmd: str, name: str, interval: int):
        if isinstance(name, str) and not name:
            raise Exception("name cannot be empty")
        elif isinstance(cmd, str) and not cmd:
            raise Exception("rule or cmd cannot be empty")

        try:
            from findex_gui.orm.models import ResourceGroup
            group = db.session.query(ResourceGroup)
            group.filter(ResourceGroup.name == "Default")
            group = group.first()
            if not group:
                raise Exception("group could not be found")

            db.session.add(NmapRule(rule=cmd, name=name, interval=interval, group=group))
            db.session.commit()
            db.session.flush()
            return True
        except:
            raise

    @staticmethod
    @role_req("ADMIN")
    def remove(uid):
        try:
            result = db.session.query(NmapRule).filter(NmapRule.id == uid).first()
            if not result:
                return True
            result.remove()
            db.session.commit()
            db.session.flush()
            return True
        except:
            raise

    @staticmethod
    @role_req("ADMIN")
    def update(uid: str, name: str = None, rule: str = None, output: str = None):
        try:
            result = db.session.query(NmapRule).filter(NmapRule.id == uid).first()
            if not result:
                raise Exception("rule not found")
            if isinstance(rule, str):
                result.rule = rule
            if isinstance(output, str):
                result.output = output
            if isinstance(name, str):
                result.name = name
            db.session.commit()
            db.session.flush()
            return True
        except:
            raise

