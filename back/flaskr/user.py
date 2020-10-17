import psycopg2
import flask_login
import hashlib


def HASH(s):
    return hashlib.md5(s.encode("utf8")).hexdigest()


class User(flask_login.UserMixin):
    def __init__(self, _id):
        self.id = _id


class UsersDAO:
    def __init__(self, dbname, user, pwd, host=None, port=None, table_name="users"):
        self.dbname = dbname
        self.table_name = table_name
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=pwd,
                                     host=host, port=port)

    def get(self, uid):
        with self.conn as conn:
            with conn.cursor() as cur:
                cur.execute(f"select * from {self.table_name} where uid = %s",
                            (uid, ))
                fetched = cur.fetchall()
        if fetched:
            uid, pwdh = fetched[0]
            return User(uid)

    def get_auth(self, uid, pwd):
        with self.conn as conn:
            with conn.cursor() as cur:
                cur.execute(f"select * from {self.table_name} where uid = %s and password = %s",
                            (uid, HASH(pwd)))
                fetched = cur.fetchall()
        if fetched:
            uid, pwdh = fetched[0]
            return User(uid)

    def add_user(self, uid, pwd):
        try:
            with self.conn as conn:
                with conn.cursor() as cur:
                    return cur.execute(f"insert into {self.table_name} values (%s, %s);", (uid, HASH(pwd)))
        except psycopg2.errors.UniqueViolation:
            pass

    def del_user(self, uid):
        with self.conn as conn:
            with conn.cursor() as cur:
                return cur.execute(f"delete from {self.table_name} where uid = %s;", (uid, ))

    def close(self):
        self.conn.close()


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
