import flask_login

class User(flask_login.UserMixin):
    def __init__(self, _id):
        self.id = _id
