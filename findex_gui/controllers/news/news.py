from findex_gui.web import db
from findex_gui.orm.models import Post, User
from findex_gui.controllers.user.user import UserController


class NewsController:
    @staticmethod
    def get(uid: int = None, limit: int = 5, offset: int = 0):
        q = db.session.query(Post)

        if isinstance(uid, int):
            return q.filter(Post.id == uid).first()
        else:
            q = q.order_by(Post.date_added.desc())

        if isinstance(limit, int):
            q = q.limit(limit)
        if isinstance(offset, int):
            q = q.offset(offset)

        return q.all()

    @staticmethod
    def add(content: str, title: str, current_user: User = None):
        if not isinstance(current_user, User):
            current_user = UserController.get_current_user()

        post = Post(content=content, title=title, created_by=current_user)
        db.session.add(post)
        db.session.commit()
        return post

    @staticmethod
    def update(uid: str, content: str = None, title: str = None):
        result = db.session.query(Post).filter(Post.id == uid).first()
        if not result:
            raise Exception("post/news not found")
        if isinstance(content, str):
            result.content = content
        if isinstance(title, str):
            result.output = title
        db.session.commit()
        db.session.flush()
        return True

    @staticmethod
    def remove(uid: int):
        result = db.session.query(Post).filter(Post.id == uid).first()
        if not result:
            raise Exception("post/news not found")
        db.session.delete(result)
        db.session.commit()
        db.session.flush()
        return True
