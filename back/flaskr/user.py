import flask_login


class User(flask_login.UserMixin):
    def __init__(self, _id):
        self.id = _id


class UserDAO:
    def __init__(self, db=None):
        self.db = db

    def get(self, uid):
        if uid == "0":
            return User("0")

    def get_auth(self, uid, pwd):
        if uid is None and pwd == "0":
            return User("0")
