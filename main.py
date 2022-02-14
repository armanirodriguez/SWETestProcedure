from flask import Flask, render_template, url_for, flash, redirect, request
from forms import procedureForm
from flask_sqlalchemy import SQLAlchemy
from models import TestProcedure
from app import db






from app import app

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title="Home Page")

@app.route("/procedures")
def procedures():
    procedures = TestProcedure.query.all()
    print(procedures)
    return render_template("procedures.html", title="Procedure", dataTable=procedures)

@app.route("/new_procedure", methods=['GET', 'POST'])
def new_procedure():
    form = procedureForm()
    # When form is submitted, create a 
    if form.validate_on_submit():
        myData = TestProcedure(form.name.data, form.version.data, form.approval.data, form.notes.data)
        db.session.add(myData)
        db.session.commit()
        flash(f'Procedure created for {form.name.data}!', 'success')
        return redirect(url_for('procedures'))
    return render_template("new_procedure.html", title="New Procedure", form=form)

if __name__ == "__main__":
    app.run(debug=True)