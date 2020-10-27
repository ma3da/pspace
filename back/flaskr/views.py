from flask import request, send_from_directory
from flask.json import jsonify
from flask_login import login_required, login_user, logout_user, current_user
from flaskr import app, dao_users, dao_defsrc, DATA_FP
import flaskr.defi as defv


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    _user = dao_users.get_auth("0", data.get("pwd", None))
    if _user is not None:
        login_user(_user)
    uid = None if current_user.is_anonymous else str(current_user.id)
    return jsonify({"logged": current_user.is_authenticated,
                    "username": uid})


@app.route("/logged", methods=["GET"])
def logged():
    uid = None if current_user.is_anonymous else str(current_user.id)
    return jsonify({"logged": current_user.is_authenticated,
                    "username": uid})


@app.route("/logout", methods=["POST"])
def logout():
    logout_user()
    return jsonify({"logged": current_user.is_authenticated})


@app.route("/")
def index():
    return send_from_directory(DATA_FP, "index.html")

@app.route("/api/words", methods=["GET"])
@login_required
def send_words():
    return jsonify(list(dao_defsrc.iter_words(limit=20)))


@app.route("/api/<word>", methods=["GET"])
@login_required
def serve(word):
    data_src = "cache"
    if defv.check_input(word):
        word = word.strip()
        raw = dao_defsrc.cache.get_raw(word)
        if raw is None:
            raw, data_src = defv.get_definition_html(word, defv.to_raw_html)
            dao_defsrc.cache.set_raw(word, raw)
        processed = dao_defsrc.cache.get_processed(word)
        if processed is None:
            processed, data_src = defv.get_definition_html(word, defv.process_article_src)
            dao_defsrc.cache.set_processed(word, processed)
    return {"htmlcontent": raw, "processed": processed, "datasource": data_src}
