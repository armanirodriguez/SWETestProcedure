from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/procedures')
def procedures():
    return render_template("procedures.html")

app.run(debug=True)