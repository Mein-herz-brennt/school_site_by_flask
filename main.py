from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def send_index():
    return render_template("index.html")


@app.route("/add_new_emp")
def new_emp():
    return render_template("add_new_emp.html")


if __name__ == '__main__':
    app.run(debug=True)
