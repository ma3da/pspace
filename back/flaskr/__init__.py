from flask import Flask

app = Flask(__name__,
            static_folder="../build/static"
            )

from flaskr import views
