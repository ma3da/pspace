from flask import Flask, send_from_directory, request
import back.views as defv

app = Flask(__name__,
            static_folder="build/static"
            )


@app.route('/')
def hello_world():
    return send_from_directory("build", "index.html")


@app.route("/api/<word>", methods=["POST"])
def serve(word):
    process_func = (defv.process_article_src_dummy if request.form.get("no_process", False)
                    else defv.process_article_src)
    html_content, data_src = "No definition found.", None
    if defv.check_input(word):
        word = word.strip()
        html_content, data_src = defv.get_definition_html(word, process_func)
    return {"htmlcontent": html_content, "datasource": data_src}
