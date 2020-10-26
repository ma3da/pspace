from sqlalchemy.sql import select, insert, update
import sqlalchemy.exc
from flaskr.tables import USERS
import flask_login
import hashlib


def HASH(s):
    return hashlib.md5(s.encode("utf8")).hexdigest()


class User(flask_login.UserMixin):
    def __init__(self, _id):
        self.id = _id


class UsersDAO:
    def __init__(self, dbname, user, pwd, host=None, port=None):
        self.dbname = dbname
        self.engine = sqlalchemy.create_engine(
            f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{dbname}")

    def get(self, uid):
        with self.engine.connect() as conn:
            s = select([USERS]).where(USERS.c.uid == uid)
            result = conn.execute(s)
            row = result.fetchone()
        if row is not None:
            uid, pwdh = row
            return User(uid)

    def get_auth(self, uid, pwd):
        with self.engine.connect() as conn:
            s = (select([USERS])
                 .where(USERS.c.uid == uid)
                 .where(USERS.c.password == HASH(pwd)))
            result = conn.execute(s)
            row = result.fetchone()
        if row is not None:
            uid, pwdh = row
            return User(uid)

    def add_user(self, uid, pwd):
        try:
            with self.engine.connect() as conn:
                s = USERS.insert().values(uid=uid, password=HASH(pwd))
                conn.execute(s)
        except sqlalchemy.exc.IntegrityError:
            pass

    def del_user(self, uid):
        with self.engine.connect() as conn:
            s = USERS.delete().where(USERS.c.uid == uid)
            conn.execute(s)

    def close(self):
        self.engine.dispose()


class UsersDummyDAO:
    def get(self, uid):
        if uid == "0":
            return User("0")

    def get_auth(self, uid, pwd):
        if uid == "0" and pwd == "0":
            return User("0")

    def add_user(self, uid, pwd):
        return 0

    def del_user(self, uid):
        return 0

    def close(self):
        pass
