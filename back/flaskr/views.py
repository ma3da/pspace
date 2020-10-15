from flask import request, send_from_directory
from flask_login import UserMixin, login_required, login_user
from flaskr import app, DATA_FP, login_manager
import flaskr.defi as defv


class User(UserMixin):
    pass


@login_manager.user_loader
def load_user(user_id):
    if user_id == "0": 
        return User(user_id)


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if data.get("pwd", None) == "0":
        login_user(user)

    return send_from_directory(DATA_FP, "index.html")


@app.route('/')
def hello_world():
    return send_from_directory(DATA_FP, "index.html")


@app.route("/api/<word>", methods=["POST"])
# @login_required
def serve(word):
    data = request.get_json()
    process_func = (defv.process_article_src if data.get("process", False)
                    else defv.process_article_src_dummy)
    html_content, data_src = "No definition found.", None
    if defv.check_input(word):
        word = word.strip()
        html_content, data_src = defv.get_definition_html(word, process_func)
    return {"htmlcontent": html_content, "datasource": data_src}
