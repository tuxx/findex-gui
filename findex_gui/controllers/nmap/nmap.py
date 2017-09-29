from findex_gui.web import db
from findex_gui.orm.models import NmapRule


class NmapController:
    @staticmethod
    def get(uid: str = None):
        try:
            if uid:
                return db.session.query(NmapRule).filter(NmapRule.id == uid).first()
            return db.session.query(NmapRule).all()
        except:
            raise

    @staticmethod
    def add(cmd: str):
        try:
            db.session.add(NmapRule(rule=cmd))
            db.session.commit()
            db.session.flush()
            return True
        except:
            raise

    @staticmethod
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
    def update(uid: str, rule: str):
        try:
            result = db.session.query(NmapRule).filter(NmapRule.id == uid).first()
            if not result:
                raise Exception("rule not found")
            result.rule = rule
            db.session.commit()
            db.session.flush()
            return True
        except:
            raise
