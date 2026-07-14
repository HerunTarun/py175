from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    with open('book_viewer/data/toc.txt', 'r') as file:
        contents = file.readlines()
    return render_template('index.html', contents=contents)

if __name__ == "__main__":
    app.run(debug=True, port=5003)