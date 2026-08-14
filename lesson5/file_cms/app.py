import os
from functools import wraps

from flask import (
    flash,
    Flask,
    render_template,
    send_from_directory,
    redirect,
    request,
    session,
    url_for
    )
from markdown import markdown

from src.file_cms.utils import (
    find_logged_in_user,
    verify_user,
    verify_user_password,
    toggle_user_login_status
    )

app = Flask(__name__)
app.secret_key = 'secret3'

@app.before_request
def initialize_session():
    if 'users' not in session:
        session['users'] = [
            {
                'admin': {
                    'password': 'secret4',
                    'logged in': False,
                }
            }
        ]

def require_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not find_logged_in_user(session['users']):
            flash("You must be logged in to do that", "error")
            return redirect(url_for('log_in'))
        else:
            result = func(*args, **kwargs)
            return result
    return wrapper

def get_data_path():
    if app.config['TESTING']:
        return os.path.join(os.path.dirname(__file__), 'tests', 'data')
    else:
        return os.path.join(os.path.dirname(__file__), 'src', 'file_cms', 'data')

@app.route("/")
def index():
    data_dir = get_data_path()
    files = [os.path.basename(path) for path in os.listdir(data_dir)]

    logged_in_user = find_logged_in_user(session['users'])

    return render_template('index.html', files=files, user=logged_in_user)

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
        return redirect(url_for('index', file_name=file_name))

@app.route("/<file_name>/edit")
@require_login
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
        return redirect(url_for('index', file_name=file_name))

@app.route("/<file_name>", methods=["POST"])
@require_login
def update_document(file_name):
    data_dir = get_data_path()
    file_path = os.path.join(data_dir, file_name)

    new_contents = request.form.get('contents', '')
    with open(file_path, 'w') as f:
        f.write(new_contents)

    flash(f"{file_name} has been updated.", "success")
    return redirect(url_for('index'))

@app.route("/new")
@require_login
def new_document():
    title = 'New Document'
    return render_template('new_document.html', title=title)

@app.route("/new", methods=["POST"])
@require_login
def create_document():
    document_name = request.form.get('document_name', '').strip()

    data_dir = get_data_path()
    new_file_path = os.path.join(data_dir, document_name)

    if len(document_name) == 0:
        flash("A name is required.", "error")
        title = 'New Document'
        return render_template('new_document.html', title=title), 422
    elif os.path.exists(new_file_path):
        flash(f"{document_name} already exists.", "error")
        title = 'New Document'
        return render_template('new_document.html', title=title), 422
    else:
        with open(new_file_path, "w") as f:
            f.write("")

        flash(f"{document_name} has been created.", "success")
        return redirect(url_for('index'))

@app.route("/<file_name>/delete", methods=["POST"])
@require_login
def delete_document(file_name):
    data_dir = get_data_path()
    file_path = os.path.join(data_dir, file_name)

    if os.path.isfile(file_path):
        os.remove(file_path)
        flash(f"{file_name} has been deleted.", "success")
    else:
        flash(f"{file_name} does not exist.", "error")

    return redirect(url_for('index'))

@app.route('/login')
def log_in():
    return render_template('login.html')

@app.route('/login', methods=["POST"])
def user_login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    if not verify_user(username, session['users']):
        flash(f"{username} does not exist.", "error")
        return render_template('login.html')
    else:
        if not verify_user_password(username, password, session['users']):
            flash(f"Invalid password.", "error")
            return render_template('login.html', username=username)
        else:
            toggle_user_login_status(username, session['users'])
            flash("Welcome!", "success")
            return redirect(url_for('index'))

@app.route('/<user>/logout', methods=["POST"])
def log_out_user(user):
    toggle_user_login_status(user, session['users'])
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True, port=5003)