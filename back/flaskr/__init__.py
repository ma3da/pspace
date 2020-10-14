from flask import Flask
import os

BASE_FP = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_FP = os.path.join(BASE_FP, "front", "build")

app = Flask(__name__,
            static_folder=os.path.join(DATA_FP, "static")
            )

from flaskr import views
