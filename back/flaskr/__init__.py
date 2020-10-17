import flask
import flask_login
import os
import flaskr.user as f_user


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
    dao_users = f_user.UsersDAO(
        dbname=os.environ.get("PSPACE_DB_NAME", hs.DB_NAME),
        user=os.environ.get("PSPACE_DB_USER", hs.DB_USER),
        pwd=os.environ.get("PSPACE_DB_PWD", hs.DB_PWD),
        host=os.environ.get("PSPACE_DB_HOST", hs.DB_HOST),
        port=os.environ.get("PSPACE_DB_PORT", hs.DB_PORT)
    )
except Exception as e:
    if "dao_users" in globals():
        dao_users.close()
    print(e)
    print("Using UserDummyDAO, no data to be read or written.")
    dao_users = f_user.UsersDummyDAO()

# !!!!!!!!!!!!!!! DEV DEV DEV !!!!!!!!!!!!!!!
dao_users.add_user("0", "0")


@login_manager.user_loader
def load_user(user_id):
    return dao_users.get(user_id)


from flaskr import views
