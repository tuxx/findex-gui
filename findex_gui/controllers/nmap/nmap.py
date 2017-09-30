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
    def add(cmd: str, name: str):
        if isinstance(name, str) and not name:
            raise Exception("name cannot be empty")
        elif isinstance(cmd, str) and not cmd:
            raise Exception("rule or cmd cannot be empty")

        try:
            db.session.add(NmapRule(rule=cmd, name=name))
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

    @staticmethod
    @role_req("ADMIN")
    def scan(cmd):
        """unsafe method, should only be called by the admin"""
        hosts = []
        try:
            results = os.popen("%s | grep open" % cmd).read()
            for line in [line.rstrip().lower() for line in results.split("\n") if line]:
                if not line.startswith("host: "):
                    continue
                spl = line.split(" ")
                host = spl[1]
                port = int(spl[3].split("/")[0])
                hosts.append([host, port])
        except Exception:
            pass
        return hosts
