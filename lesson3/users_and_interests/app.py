from flask import Flask, render_template, redirect, url_for
import yaml

app = Flask(__name__)

with open('users.yaml', 'r') as file:
    user_data = yaml.safe_load(file)

def total_interests():
    total_users = len(user_data)
    interest_count = sum([1 for person in user_data.values()
                           for _ in person['interests']])
    return total_users, interest_count

@app.route('/')
def index():
    return redirect(url_for('users'))

@app.route('/users')
def users():
    people, interests = total_interests()
    return render_template('users_list.html',
                           contents=user_data,
                           people=people,
                           interests=interests)

@app.route('/<user>')
def user(user):
    people, interests = total_interests()
    return render_template('user.html',
                           user=user,
                           contents=user_data,
                           people=people,
                           interests=interests)

if __name__ == '__main__':
    app.run(debug=True, port=5003)