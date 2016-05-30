from flask import request, redirect, url_for

from findex_gui import app, db, themes
from findex_gui.orm.models import Users


class AuthController:
    def __init__(self):
        pass

    def register(self, username, password):
        if Users.query.filter(Users.username == username).first():
            return 'User already exists.'

        user = Users(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        return user

    def login(self, username, password):
        try:
            user = Users.query.filter(Users.username == username).one()
            return user.authenticate(password)
        except:
            pass
