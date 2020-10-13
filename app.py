from flask import Flask, send_from_directory

app = Flask(__name__,
            static_folder="build/static"
            )


@app.route('/')
def hello_world():
    return send_from_directory("build", "index.html")


@app.route("/api/<word>", methods=["POST"])
def serve(word):
    return {"htmldefinition": f"looking for a definition: {word}"}
