import flask
import flask_login
import os
import flaskr.dao as dao
from flaskr.user import User
from . import config
import sqlalchemy
import redis
import logging

BACK_FP = os.path.dirname(os.path.dirname(__file__))
CONF_FP = os.path.join(BACK_FP, "conf")
LOG_FP = os.path.join(BACK_FP, "back.log")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(LOG_FP)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("starting...")
config.load_config(CONF_FP if os.path.exists(CONF_FP) else None)
login_manager = flask_login.LoginManager()
app = flask.Flask(__name__)
app.secret_key = config.get("SECRET_KEY", _raise=True)
login_manager.init_app(app)

try:
    redis_client = redis.Redis(**dao.util.find_params_dict("host", "port", namespace="CACHE"))
    cache = dao.Cache(redis_client)
except Exception as e:
    if "redis_client" in globals():
        redis_client.close()
    logger.info(e)
    logger.info("Using dummy cache...")
    cache = dao.DummyCache()

try:
    dbname, user, pwd, host, port = \
        dao.util.find_params("name", "user", "pwd", "host", "port", namespace="DB")

    db_engine = sqlalchemy.create_engine(
        f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{dbname}")

    dao_users = dao.UsersDAO(db_engine, User)
    dao_defsrc = dao.DefinitionSrcDAO(db_engine, cache)
except Exception as e:
    if "db_engine" in globals():
        db_engine.dispose()
    logger.info(e)
    logger.info("Using dummy daos, no data to be read or written...")
    dao_users = dao.UsersDummyDAO(User)
    dao_defsrc = dao.DefinitionSrcDummyDAO(cache)


@login_manager.user_loader
def load_user(user_id):
    return dao_users.get(user_id)


from flaskr import views
