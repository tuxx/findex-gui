from sqlalchemy import desc

from findex_gui.web import db
from findex_gui.orm.models import Logging


class LogController:
    @staticmethod
    def get(category: str = None, limit: int = 10, offset: int = 0):
        q = db.session.query(Logging)

        if isinstance(category, str):
            q = q.filter(Logging.category == category)

        q = q.order_by(desc(Logging.date_added))

        if isinstance(limit, int):
            q = q.limit(limit)

        if isinstance(offset, int):
            q = q.offset(offset)

        return q.all()
