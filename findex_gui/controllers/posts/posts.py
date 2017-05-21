from findex_gui.web import db
from findex_gui.orm.models import Post, User
from findex_gui.controllers.user.roles import role_req


class PostController:
    @staticmethod
    @role_req("ADMIN")
    def add(content: str, title: str, current_user: User):
        post = Post(content=content, title=title, created_by=current_user)
        db.session.add(post)
        db.session.commit()
        return post

    @staticmethod
    def get(limit: int = 5, offset: int = 0):
        q = db.session.query(Post)
        q = q.order_by(Post.date_added.desc())
        q = q.limit(limit)
        q = q.offset(offset)
        return q.all()
