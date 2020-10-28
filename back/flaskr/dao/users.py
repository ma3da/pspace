from sqlalchemy.sql import select, insert, update
import sqlalchemy.exc
from .tables import USERS
import hashlib


def HASH(s):
    return hashlib.md5(s.encode("utf8")).hexdigest()


class UsersDAO:
    def __init__(self, engine, user_class):
        self.engine = engine
        self.user_class = user_class

    def get(self, uid):
        with self.engine.connect() as conn:
            s = select([USERS]).where(USERS.c.uid == uid)
            result = conn.execute(s)
            row = result.fetchone()
        if row is not None:
            uid, pwdh = row
            return self.user_class(uid)

    def get_auth(self, uid, pwd):
        with self.engine.connect() as conn:
            s = (select([USERS])
                 .where(USERS.c.uid == uid)
                 .where(USERS.c.password == HASH(pwd)))
            result = conn.execute(s)
            row = result.fetchone()
        if row is not None:
            uid, pwdh = row
            return self.user_class(uid)

    def add_user(self, uid, pwd):
        try:
            with self.engine.connect() as conn:
                s = USERS.insert().values(uid=uid, password=HASH(pwd))
                return conn.execute(s)
        except sqlalchemy.exc.IntegrityError:
            pass

    def del_user(self, uid):
        with self.engine.connect() as conn:
            s = USERS.delete().where(USERS.c.uid == uid)
            return conn.execute(s)


class UsersDummyDAO:
    def __init__(self, user_class):
        self.user_class = user_class

    def get(self, uid):
        if uid == "0":
            return self.user_class("0")

    def get_auth(self, uid, pwd):
        if uid == "0" and pwd == "0":
            return self.user_class("0")

    def add_user(self, uid, pwd):
        return 0

    def del_user(self, uid):
        return 0
