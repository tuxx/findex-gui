from flask import request, redirect, url_for

from findex_gui import app, db, themes
from findex_gui.orm.models import User


class AuthController:
    def __init__(self):
        pass

    def register(self, username, password):
        if User.query.filter(User.username == username).first():
            return 'User already exists.'

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        return user

    def login(self, username, password):
        try:
            user = User.query.filter(User.username == username).one()
            return user.authenticate(password)
        except:
            pass