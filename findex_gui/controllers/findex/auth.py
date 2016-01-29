from bottle import auth_basic, request, HTTPError
import random, hashlib, os
from passlib.handlers.sha2_crypt import sha512_crypt
from findex_gui.db.orm import Postgres, Users


def basic_auth():
    def check(user, password):
        if user == 'admin' and password == 'admin':
            return True

    def err():
        err = HTTPError(401, "Access denied")
        err.add_header('WWW-Authenticate', 'Basic realm="%s"' % "admin area")
        return err

    user, password = request.auth or (None, None)
    if user is None or not check(user, password):
        return err()


class Auth():
    def __init__(self, db):
        self.db = db

    def make_password(self, password):
        return sha512_crypt.encrypt(password)

    def check_password(self, name, password):
        usr = self.db.query(Users).filter(Users.name == name).first()
        if usr and usr.name:
            return sha512_crypt.verify(password, usr.password)

    def change_password(self, name, old_password, password):
        if self.check_password(name, old_password) and password:
            usr = self.db.query(Users).filter(Users.name == name).first()
            usr.password = self.make_password(password)
            self.db.commit()

            return True
