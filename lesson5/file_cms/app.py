from flask import (
    flash,
    Flask,
    render_template,
    send_from_directory,
    redirect,
    request,
    url_for
    )
from markdown import markdown
import os

app = Flask(__name__)
app.secret_key = 'secret2'
def get_data_path():
    if app.config['TESTING']:
        return os.path.join(os.path.dirname(__file__), 'tests', 'data')
    else:
        return os.path.join(os.path.dirname(__file__), 'src', 'file_cms', 'data')

@app.route("/")
def index():
    root = os.path.abspath(os.path.dirname(__file__))
    data_dir = get_data_path()
    files = [os.path.basename(path) for path in os.listdir(data_dir)]

    return render_template('index.html', files=files)

@app.route("/<file_name>")
def document(file_name):
    data_dir = get_data_path()
    file_path = os.path.join(data_dir, file_name)

    if os.path.isfile(file_path):
        if file_name.endswith('.md'):
            with open(file_path, "r") as f:
                contents = f.read()
            return render_template('markdown.html',
                                   contents=markdown(contents))
        else:
            return send_from_directory(data_dir, file_name)
    else:
        flash(f"{file_name} does not exist.", "error")
        return redirect(url_for('index', file_name = file_name))

@app.route("/<file_name>/edit")
def edit_document(file_name):
    data_dir = get_data_path()
    file_path = os.path.join(data_dir, file_name)

    if os.path.isfile(file_path):
        with open(file_path, "r") as f:
            contents = f.read()
        return render_template('edit_document.html',
                           file_name=file_name,
                           contents=contents)
    else:
        flash(f"{file_name} does not exist.", "error")
        return redirect(url_for('index', file_name = file_name))

@app.route("/<file_name>", methods=["post"])
def update_document(file_name):
    data_dir = get_data_path()
    file_path = os.path.join(data_dir, file_name)

    new_contents = request.form['contents']
    with open(file_path, 'w') as f:
        f.write(new_contents)

    flash(f"{file_name} has been updated.", "success")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port=5003)