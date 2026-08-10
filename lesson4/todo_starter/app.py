from uuid import uuid4
from flask import (
    flash,
    Flask,
    redirect,
    render_template,
    request, session,
    url_for,
)
from utils import error_for_list_title, find_list_by_id, error_for_todo_title
from werkzeug.exceptions import NotFound

app = Flask(__name__)
app.secret_key='secret1'

@app.before_request
def initialize_session():
    if 'lists' not in session:
        session['lists'] = []

@app.route("/")
def index():
    return redirect(url_for('get_lists'))

@app.route('/lists/new')
def add_todo_list():
    return render_template('new_list.html')

@app.route('/lists')
def get_lists():
    return render_template("lists.html", lists=session['lists'])

@app.route('/lists', methods=['POST'])
def create_list():
    title = request.form["list_title"].strip()

    error = error_for_list_title(title, session['lists'])
    if error:
        flash(error, "error")
        return render_template('new_list.html', title=title)

    session['lists'].append({
            'id': str(uuid4()),
            'title': title,
            'todos': [],
    })

    flash("The list has been created.", "success")
    session.modified = True
    return redirect(url_for('get_lists'))

@app.route('/lists/<list_id>')
def display_todo_list(list_id):
    todo_list = find_list_by_id(list_id, session['lists'])

    if not todo_list:
        raise NotFound("This is not the list you're looking for")

    return render_template('list.html', list=todo_list)

@app.route('/lists/<list_id>/todos', methods=['POST'])
def create_todo(list_id):
    title = request.form["todo"].strip()

    todo_list = find_list_by_id(list_id, session['lists'])
    if not todo_list:
            raise NotFound("This is not the list you're looking for")


    error = error_for_todo_title(title)
    if error:
        flash(error, "error")
        return render_template('list.html', list=todo_list)

    todo_list['todos'].append({
        'id': str(uuid4()),
        'title': title,
        'completed': False,
    })

    flash("The todo was added.", "success")
    session.modified = True

    return redirect(url_for("display_todo_list", list_id=list_id))

if __name__ == "__main__":
    app.run(debug=True, port=5003)