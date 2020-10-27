import flask
import flask_login
import os
import flaskr.dao as dao
from flaskr.user import User
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

try:
    import flaskr.nocommit.hiddensettings as hs

    host = os.environ.get("PSPACE_CACHE_HOST", hs.CACHE_HOST)
    port = os.environ.get("PSPACE_CACHE_PORT", hs.CACHE_PORT)
    redis_client = redis.Redis(host=host, port=port)
    cache = dao.Cache(redis_client)
except Exception as e:
    if "redis_client" in globals():
        redis_client.close()
    print(e)
    print("Using dummy daos, no data to be read or written.")
    cache = dao.DummyCache()

try:
    import flaskr.nocommit.hiddensettings as hs

    dbname = os.environ.get("PSPACE_DB_NAME", hs.DB_NAME)
    user = os.environ.get("PSPACE_DB_USER", hs.DB_USER)
    pwd = os.environ.get("PSPACE_DB_PWD", hs.DB_PWD)
    host = os.environ.get("PSPACE_DB_HOST", hs.DB_HOST)
    port = os.environ.get("PSPACE_DB_PORT", hs.DB_PORT)

    db_engine = sqlalchemy.create_engine(
        f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{dbname}")

    dao_users = dao.UsersDAO(db_engine, User)
    dao_defsrc = dao.DefinitionSrcDAO(db_engine, cache)
except Exception as e:
    if "db_engine" in globals():
        db_engine.dispose()
    print(e)
    print("Using dummy daos, no data to be read or written.")
    dao_users = dao.UsersDummyDAO(User)
    dao_defsrc = dao.DefinitionSrcDummyDAO(cache)

# !!!!!!!!!!!!!!! DEV DEV DEV !!!!!!!!!!!!!!!
dao_users.add_user("0", "0")


@login_manager.user_loader
def load_user(user_id):
    return dao_users.get(user_id)


from flaskr import views
