from flask import Flask, render_template, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy

from app.forms import *
from app.models import *
from app import db
from app import app

@app.before_first_request
def create_tables():
    db.create_all()

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title="Home Page")

@app.route("/procedures")
def procedures():
    procedures = TestProcedure.query.all()
    return render_template("procedures.html", title="Procedure", procedures=procedures)

@app.route("/procedure/<int:id>")
def procedure(id):
    current_procedure = TestProcedure.query.get_or_404(id)
    steps = current_procedure.steps
    print(steps)
    return render_template("teststeps.html", procedure=current_procedure)

@app.route("/procedure/<int:procedure_id>/newstep", methods=['GET','POST'])
def new_step(procedure_id):
    form = StepForm()
    if form.validate_on_submit():
        step_name = form.step_name.data
        instructions = form.instructions.data
        pass_condition = form.pass_condition.data
        new_step = TestStep(name=step_name,
                            procedure_id=procedure_id,
                            instructions=instructions,
                            pass_condition=pass_condition)
        db.session.add(new_step)
        db.session.commit()
        return redirect(url_for('procedure',id=procedure_id))
    return render_template("newstep.html", title="New Step", form=form, id=procedure_id)



@app.route("/newprocedure", methods=['GET', 'POST'])
def new_procedure():
    form = ProcedureForm()
    if form.validate_on_submit():
        procedure_name = form.procedure_name.data
        approval = form.approval.data
        notes = form.notes.data
        myData = TestProcedure(name = procedure_name,
                               approval = approval,
                               notes = notes)
        db.session.add(myData)
        db.session.commit()

        flash(f'Procedure {procedure_name} created successfully!', 'success')

        return redirect(url_for('procedures'))
    return render_template("new_procedure.html", title="New Procedure", form=form)

@app.route("/edit/<int:id>", methods=['GET', 'POST'])
def edit(id):
    editForm = ProcedureForm()
    editProd = TestProcedure.query.get_or_404(id)
    editForm.formApproval.checked = editProd.approval
    if editForm.validate_on_submit():
        editProd.name = editForm.procedure_name.data
        editProd.approval = editForm.approval.data
        editProd.notes = editForm.notes.data

        db.session.commit()
        flash(f'Procedure {editForm.procedure_name.data} updated!', 'dark')
        return redirect(url_for('procedures'))
    return render_template("edit.html", title="Edit Procedure", editForm=editForm, editProd=editProd)

@app.route("/delete_procedure/<int:id>", methods=['POST'])
def delete_procedure(id):
    procedure = TestProcedure.query.get_or_404(id)
    db.session.delete(procedure)
    db.session.commit()
    flash("Procedure successfully deleted!",'success')
    return redirect(url_for('procedures'))

@app.route("/deletestep/<int:id>", methods=['POST'])
def delete_step(id):
    step = TestStep.query.get_or_404(id)
    procedure_id = step.procedure_id
    db.session.delete(step)
    db.session.commit()
    flash("Step successfully deleted!",'success')
    return redirect(url_for('procedure',id=procedure_id))

@app.route("/procedure/<int:id>/run", methods=['POST','GET'])
def run_test_procedure(id):
    procedure = TestProcedure.query.get_or_404(id)
    procedure_name = procedure.name
    steps = procedure.steps
    if len(steps) == 0:
        flash("There are currently no test steps to run", "warning")
        return redirect(url_for('procedure', id=id))
    form = TestRunFormFactory(steps).get_test_run_form()
    if form.validate_on_submit():
        for field_name,value in form.data.items():
            try:
                step_id = int(field_name)
            except ValueError:
                continue
            test_step = TestStep.query.get(step_id)
            if value == "pass":
                test_step.status = 1
            elif value == "fail":
                test_step.status = -1
        db.session.commit()
        flash("Test run completed",'success')
        return redirect(url_for('procedure', id=id))
    return render_template("runtest.html", id=id, form=form, steps=steps, procedure_name=procedure_name)

    
    
    

if __name__ == "__main__":
    app.run(debug=True)