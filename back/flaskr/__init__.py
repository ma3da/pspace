from flask import Flask
import flask_login
import os

BASE_FP = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_FP = os.path.join(BASE_FP, "front", "build")

login_manager = flask_login.LoginManager()
app = Flask(__name__,
            static_folder=os.path.join(DATA_FP, "static")
            )
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
login_manager.init_app(app)

from flaskr import views
