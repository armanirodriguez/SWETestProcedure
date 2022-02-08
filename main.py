from flask import Flask, render_template, url_for

app = Flask(__name__)

# example test data
data = [
#   id  name            version      approved   
    [1, "Login",        1.0,        True],
    [2, "Registration", 1.0,        False],
    [3, "Payment",      1.0,        True]
]



@app.route('/')
def home():
    return render_template("home.html", title="Home Page")

@app.route('/procedures')
def procedures():
    return render_template("procedures.html", title="Procedures", data=data)

if __name__ == "__main__":
    app.run(debug=True)