from flask import (
    flash,
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from functools import wraps
from uuid import uuid4
from utils import (
    delete_todo_by_id,
    error_for_list_title,
    error_for_todo_title,
    find_list_by_id,
    find_todo_by_id,
    is_list_completed,
    is_todo_completed,
    mark_all_complete,
    sort_items,
    todos_remaining,
)
from werkzeug.exceptions import NotFound

app = Flask(__name__)
app.secret_key='secret1'

@app.context_processor
def list_utilities_processor():
    return dict(
        is_list_completed=is_list_completed
    )

def require_list(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        list_id = kwargs.get('list_id')
        todo_list = find_list_by_id(list_id, session['lists'])
        if not todo_list:
            raise NotFound("This is not the list you're looking for")
        return func(todo_list=todo_list, *args, **kwargs)
    return wrapper

def require_todo(func):
    @wraps(func)
    @require_list
    def wrapper(todo_list, *args, **kwargs):
        todo_id = kwargs.get('todo_id')
        todo = find_todo_by_id(todo_id, todo_list['todos'])
        if not todo:
            raise NotFound("This todo does not exist")
        return func(todo_list=todo_list, todo=todo, *args, **kwargs)
    return wrapper

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
    lists = sort_items(session['lists'], is_list_completed)
    return render_template("lists.html",
                           lists=lists,
                           todos_remaining=todos_remaining)

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
@require_list
def display_todo_list(list_id, todo_list):
    todo_list['todos'] = sort_items(todo_list['todos'], is_todo_completed)
    return render_template('list.html', list=todo_list)

@app.route('/lists/<list_id>/todos', methods=['POST'])
@require_list
def create_todo(list_id, todo_list):
    title = request.form["todo"].strip()

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

@app.route('/lists/<list_id>/todos/<todo_id>/toggle', methods=['POST'])
@require_todo
def update_todo_status(list_id, todo_id, todo_list, todo):
    todo['completed'] = (request.form['completed'] == 'True')

    flash("Todo updated", "success")
    session.modified = True

    return redirect(url_for("display_todo_list", list_id=list_id))

@app.route('/lists/<list_id>/todos/<todo_id>/delete', methods=['POST'])
@require_todo
def delete_todo(list_id, todo_id, todo_list, todo):
    delete_todo_by_id(todo_id, todo_list)

    flash("Todo deleted", "success")
    session.modified = True

    return redirect(url_for("display_todo_list", list_id=list_id))

@app.route('/lists/<list_id>/complete_all', methods=['POST'])
@require_list
def complete_all(list_id, todo_list):
    mark_all_complete(todo_list)

    flash("All todos completed", "success")
    session.modified = True

    return redirect(url_for("display_todo_list", list_id=list_id))

@app.route('/lists/<list_id>/edit')
@require_list
def view_edit_list(list_id, todo_list):
    return render_template('edit_list.html', list=todo_list)

@app.route('/lists/<list_id>/delete', methods=['POST'])
@require_list
def delete_list(list_id, todo_list):
    session['lists'] = [lst for lst in session['lists']
                        if lst['id'] != list_id]

    flash("The list has been deleted", "success")
    session.modified = True

    return redirect(url_for('get_lists'))

@app.route('/lists/<list_id>', methods=['POST'])
@require_list
def update_list_name(list_id, todo_list):
    title = request.form['list_title'].strip()

    error = error_for_list_title(title, session['lists'])
    if error:
        flash(error, "error")
        return render_template('edit_list.html', list=todo_list, title=title)

    todo_list['title'] = title
    flash("List name has been updated", "success")
    session.modified = True

    return redirect(url_for("display_todo_list", list_id=list_id))


if __name__ == "__main__":
    app.run(debug=True, port=5003)