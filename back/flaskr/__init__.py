import flask
import flask_login
import os
import flaskr.dao as dao
import flaskr.user as f_user
import sqlalchemy


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
    dbname = os.environ.get("PSPACE_DB_NAME", hs.DB_NAME)
    user = os.environ.get("PSPACE_DB_USER", hs.DB_USER)
    pwd = os.environ.get("PSPACE_DB_PWD", hs.DB_PWD)
    host = os.environ.get("PSPACE_DB_HOST", hs.DB_HOST)
    port = os.environ.get("PSPACE_DB_PORT", hs.DB_PORT)

    db_engine = sqlalchemy.create_engine(
            f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{dbname}")

    dao_users = f_user.UsersDAO(db_engine)
    dao_defsrc = dao.DefinitionSrcDao(db_engine)
except Exception as e:
    db_engine.dispose()
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
