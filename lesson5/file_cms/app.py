from flask import (
    flash,
    Flask,
    render_template,
    send_from_directory,
    redirect,
    url_for
    )
import os

app = Flask(__name__)
app.secret_key = 'secret2'

@app.route("/")
def index():
    root = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(root, "src", "file_cms", "data",)
    files = [os.path.basename(path) for path in os.listdir(data_dir)]

    return render_template('index.html', files=files)

@app.route("/<file_name>")
def document(file_name):
    root = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(root, "src", "file_cms", "data")
    file_path = os.path.join(data_dir, file_name)

    if os.path.isfile(file_path):
        return send_from_directory(data_dir, file_name)
    else:
        flash(f"{file_name} does not exist", "error")
        return redirect(url_for('index', file_name = file_name))


if __name__ == "__main__":
    app.run(debug=True, port=5003)