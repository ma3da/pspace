from flask import request, send_from_directory
from flask.json import jsonify
from flask_login import login_required, login_user, logout_user, current_user
from flaskr import app, user_dao, DATA_FP
import flaskr.defi as defv


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    _user = user_dao.get_auth(None, data.get("pwd", None))
    if _user is not None:
        login_user(_user)
    return jsonify({"logged": current_user.is_authenticated})


@app.route("/logged", methods=["GET"])
def logged():
    return jsonify({"logged": current_user.is_authenticated})


@app.route("/logout", methods=["POST"])
def logout():
    logout_user()
    return jsonify({"logged": current_user.is_authenticated})


@app.route("/")
def index():
    return send_from_directory(DATA_FP, "index.html")


@app.route("/api/<word>", methods=["POST"])
@login_required
def serve(word):
    data = request.get_json()
    process_func = (defv.process_article_src if data.get("process", False)
                    else defv.process_article_src_dummy)
    html_content, data_src = "No definition found.", None
    if defv.check_input(word):
        word = word.strip()
        html_content, data_src = defv.get_definition_html(word, process_func)
    return {"htmlcontent": html_content, "datasource": data_src}
