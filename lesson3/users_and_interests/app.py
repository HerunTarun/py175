from flask import Flask, render_template, redirect, g
import yaml

app = Flask(__name__)

def total_interests():
    total_users = len(g.contents)
    total_interests = sum([1 for person in g.contents.values()
                           for _ in person['interests']])
    return total_users, total_interests

@app.before_request
def load_contents():
    with open('users.yaml', 'r') as file:
        g.contents = yaml.safe_load(file)

@app.route('/')
def index():
    return redirect('/users')

@app.route('/users')
def users():
    return render_template('users_list.html', contents=g.contents)

@app.route('/<user>')
def user(user):
    people, interests = total_interests()
    return render_template('user.html',
                           user=user,
                           contents=g.contents,
                           people=people,
                           interests=interests)

if __name__ == '__main__':
    app.run(debug=True, port=5003)