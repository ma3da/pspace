import flask
import flask_login
import os
import flaskr.dao as dao
import flaskr.user as f_user
import sqlalchemy
import redis


BASE_FP = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_FP = os.path.join(BASE_FP, "front", "build")

login_manager = flask_login.LoginManager()
app = flask.Flask(
    __name__,
    static_folder=os.path.join(DATA_FP, "static")
)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
login_manager.init_app(app)


class Cache:
    key_src = "src"
    key_processed = "proc"
    key_raw = "raw"

    def __init__(self, client):
        self.client = client

    def _get(self, hsh, key):
        r = self.client.hget(hsh, key)
        if r is not None:
            if isinstance(r, bytes):
                r = r.decode("utf8")
            return r

    def _set(self, hsh, key, val):
        return self.client.hset(hsh, key, val)

    def get_src(self, word):
        return self._get(word, self.key_src)

    def set_src(self, word, src):
        return self._set(word, self.key_src, src)

    def get_processed(self, word):
        return self._get(word, self.key_processed)

    def set_processed(self, word, processed):
        return self._set(word, self.key_processed, processed)

    def get_raw(self, word):
        return self._get(word, self.key_raw)

    def set_raw(self, word, raw):
        return self._set(word, self.key_raw, raw)

try:
    import flaskr.nocommit.hiddensettings as hs

    host = os.environ.get("PSPACE_CACHE_HOST", hs.CACHE_HOST)
    port = os.environ.get("PSPACE_CACHE_PORT", hs.CACHE_PORT)
    redis_client = redis.Redis(host=host, port=port)
    cache = Cache(redis_client)

    dbname = os.environ.get("PSPACE_DB_NAME", hs.DB_NAME)
    user = os.environ.get("PSPACE_DB_USER", hs.DB_USER)
    pwd = os.environ.get("PSPACE_DB_PWD", hs.DB_PWD)
    host = os.environ.get("PSPACE_DB_HOST", hs.DB_HOST)
    port = os.environ.get("PSPACE_DB_PORT", hs.DB_PORT)

    db_engine = sqlalchemy.create_engine(
        f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{dbname}")

    dao_users = f_user.UsersDAO(db_engine)
    dao_defsrc = dao.DefinitionSrcDao(db_engine, cache)
except Exception as e:
    if "db_engine" in globals():
        db_engine.dispose()
    if "redis_client" in globals():
        redis_client.close()
    print(e)
    print("Using dummy daos, no data to be read or written.")
    dao_users = f_user.UsersDummyDAO()
    dao_defsrc = dao.DummyDao()

# !!!!!!!!!!!!!!! DEV DEV DEV !!!!!!!!!!!!!!!
dao_users.add_user("0", "0")


@login_manager.user_loader
def load_user(user_id):
    return dao_users.get(user_id)


from flaskr import views
