from flask import request, send_from_directory
from flask.json import jsonify
from flask_login import login_required, login_user, logout_user, current_user
from flaskr import app, dao_users, dao_defsrc
import flaskr.defi as defv
import logging


logger = logging.getLogger(__name__)


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    _user = None
    if "uid" in data and "pwd" in data:
        _user = dao_users.get_auth(data["uid"], data["pwd"])
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


@app.route("/api/words", methods=["GET"])
@login_required
def send_words():
    return jsonify(list(dao_defsrc.iter_words(limit=20)))


@app.route("/api/<word>", methods=["GET"])
@login_required
def serve(word):
    raw, processed, datasource = None, None, None
    if defv.check_input(word):
        datasources = []
        word = word.strip()

        raw = dao_defsrc.cache.get_raw(word)
        if raw is None:
            raw, _ds = defv.get_definition_html(word, defv.to_raw_html)
            datasources.append(_ds)
            dao_defsrc.cache.set_raw(word, raw)
        processed = dao_defsrc.cache.get_processed(word)
        if processed is None:
            processed, _ds = defv.get_definition_html(word, defv.process_article_src)
            datasources.append(_ds)
            dao_defsrc.cache.set_processed(word, processed)

        if not datasources:
            datasource = "cache"
        else: # local or remote
            datasource = sorted(datasources, reverse=True)[0]

    return jsonify({"htmlcontent": raw, "processed": processed, "datasource": datasource})


@app.route("/createuser/<u>/<p>")
@login_required
def createuser(u, p):
    if dao_users.add_user(u, p):
        logger.debug(f"creating user {u}: success")
        return f"Hello, {u}"
    logger.debug(f"creating user {u}: failure")
    return ""
