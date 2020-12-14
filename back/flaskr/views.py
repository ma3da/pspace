from flask import request, send_from_directory
from flask.json import jsonify
from flask_login import login_required, login_user, logout_user, current_user
from flaskr import app, dao_users, dao_defsrc
import flaskr.defi as defv
import logging


logger = logging.getLogger(__name__)
ANONYMOUS_WAIT = 10


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


################################ Word API ################################


@app.route("/api/words", methods=["GET"])
def send_words():
    return jsonify(list(dao_defsrc.iter_words(limit=20)))


@app.route("/api/<word>", methods=["GET"])
def serve(word):
    word = word.strip()
    if not defv.check_input(word):
        return {}

    anon_allowed = dao_defsrc.cache.elapsed_since_last_access() > ANONYMOUS_WAIT
    raw, processed, datasource = None, None, None
    raw, processed = dao_defsrc.cache.get_both(word)
    if raw or processed:
        datasource = "cache"
    elif current_user.is_authenticated or anon_allowed:
        datasources = []
        raw, _ds = defv.get_definition(word, defv.to_raw_html, raw=True)
        datasources.append(_ds)
        dao_defsrc.cache.set_raw(word, raw)
        processed, _ds = defv.get_definition(word, defv.process_article_src, raw=False)
        datasources.append(_ds)
        dao_defsrc.cache.set_processed(word, processed)
        datasource = sorted(datasources, reverse=True)[0]  # local or remote

    logger.debug(f"serving '{word}' from {datasource}")

    return jsonify({"htmlcontent": raw, "processed": processed, "datasource": datasource})


############################## DEBUG ##############################


@app.route("/createuser/<u>/<p>")
def createuser(u, p):
    if dao_users.add_user(u, p):
        logger.debug(f"creating user {u}: success")
        return f"Hello, {u}"
    logger.debug(f"creating user {u}: failure")
    return ""


@app.route("/refresh/<word>", methods=["GET"])
def recompute_and_serve(word):
    word = word.strip()
    if not defv.check_input(word):
        return {}

    anon_allowed = dao_defsrc.cache.elapsed_since_last_access() > ANONYMOUS_WAIT
    raw, processed, datasource = None, None, None
    if current_user.is_authenticated or anon_allowed:
        datasources = []
        raw, _ds = defv.get_definition(word, defv.to_raw_html, raw=True)
        datasources.append(_ds)
        dao_defsrc.cache.set_raw(word, raw)
        processed, _ds = defv.get_definition(word, defv.process_article_src, raw=False)
        datasources.append(_ds)
        dao_defsrc.cache.set_processed(word, processed)
        datasource = sorted(datasources, reverse=True)[0]  # local or remote

    logger.debug(f"serving '{word}' from {datasource}")

    return jsonify({"htmlcontent": raw, "processed": processed, "datasource": datasource})
