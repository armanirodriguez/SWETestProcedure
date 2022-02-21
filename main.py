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
    return render_template("procedures.html", title="Procedure", dataTable=procedures)

@app.route("/new_procedure", methods=['GET', 'POST'])
def new_procedure():
    form = procedureForm()
    # When form is submitted, create a 
    if form.validate_on_submit():
        myData = TestProcedure(form.formCreatedBy.data, form.formDateCreated.data, form.formProdName.data, form.formRequirements.data, form.formStatus.data, form.formPriority.data,
                                form.formEstTime.data, form.formVersion.data, form.formApproval.data, form.formNotes.data)
        db.session.add(myData)
        db.session.commit()
        flash(f'Procedure created for {form.formProdName.data}!', 'success')
        return redirect(url_for('procedures'))
    return render_template("new_procedure.html", title="New Procedure", form=form)

@app.route("/edit/<int:id>", methods=['GET', 'POST'])
def edit(id):
    editForm = procedureForm()
    editProd = TestProcedure.query.get_or_404(id)
    editForm.formApproval.checked = editProd.approval
    if editForm.validate_on_submit():
        editProd.createdBy = editForm.formCreatedBy.data
        editProd.dateCreated = editForm.formDateCreated.data
        editProd.prodName = editForm.formProdName.data
        editProd.requirements = editForm.formRequirements.data
        editProd.status = editForm.formStatus.data
        editProd.priority = editForm.formPriority.data
        editProd.estTimeToComplete = editForm.formEstTime.data
        editProd.version = editForm.formVersion.data
        editProd.approval = editForm.formApproval.data
        editProd.notes = editForm.formNotes.data

        db.session.commit()
        flash(f'Procedure {editForm.formProdName.data} updated!', 'dark')
        return redirect(url_for('procedures'))
    return render_template("edit.html", title="Edit Procedure", editForm=editForm, editProd=editProd)


if __name__ == "__main__":
    app.run(debug=True)