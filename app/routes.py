from flask import render_template, url_for, flash, redirect

from app.forms import ProcedureForm, StepForm, ProjectForm, get_test_run_form
from app.models import TestProcedure, TestStep, Project, TestRun
from app import db
from app import app


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title="Home Page")


# ===== Projects ===== #
@app.route("/projects", methods=["GET", "POST"])
def projects():
    form = ProjectForm()
    if form.validate_on_submit():
        new_project = Project(name=form.project_name.data)
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for("projects"))
    projects = Project.query.all()
    return render_template(
        "projects.html", title="projects", form=form, projects=projects
    )


@app.route("/deleteproject/<int:project_id>", methods=["POST"])
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash("Project successfully deleted!", "success")
    return redirect(url_for("projects"))


@app.route("/editproject/<int:project_id>", methods=["GET", "POST"])
def edit_project(project_id):
    editForm = ProjectForm()
    project = Project.query.get_or_404(project_id)
    print(editForm.project_name.data)
    if editForm.validate_on_submit():
        project.name = editForm.project_name.data
        db.session.commit()
    return redirect(url_for("projects"))


# ===== Test Procedures ===== #
@app.route("/project/<int:project_id>/procedures")
def procedures(project_id):
    procedures = Project.query.get_or_404(project_id).procedures
    return render_template(
        "procedures.html",
        title="Procedure",
        procedures=procedures,
        project_id=project_id,
    )


@app.route("/project/<int:project_id>/newprocedure", methods=["GET", "POST"])
def new_procedure(project_id):
    form = ProcedureForm()
    if form.validate_on_submit():
        procedure_name = form.procedure_name.data
        approval = form.approval.data
        approvalNotes = form.approvalNotes.data
        notes = form.notes.data
        myData = TestProcedure(
            name=procedure_name,
            approval=approval,
            approvalNotes=approvalNotes,
            notes=notes,
            project_id=project_id,
        )
        db.session.add(myData)
        db.session.commit()

        flash(f"Procedure {procedure_name} created successfully!", "success")

        return redirect(url_for("procedures", project_id=project_id))
    return render_template(
        "newprocedure.html", title="New Procedure", form=form, project_id=project_id
    )


@app.route("/editprocedure/<procedure_id>", methods=["GET", "POST"])
def edit_procedure(procedure_id):
    editForm = ProcedureForm()
    edit_procedure = TestProcedure.query.get_or_404(procedure_id)
    editForm.approval.checked = edit_procedure.approval
    if editForm.validate_on_submit():
        edit_procedure.name = editForm.procedure_name.data
        edit_procedure.approval = editForm.approval.data
        edit_procedure.notes = editForm.notes.data
        edit_procedure.approvalNotes = editForm.approvalNotes.data
        db.session.commit()
        flash(f"Procedure {editForm.procedure_name.data} updated!", "dark")
        return redirect(url_for("procedures", project_id=edit_procedure.project_id))
    return render_template(
        "editprocedure.html",
        title="Edit Procedure",
        editForm=editForm,
        edit_procedure=edit_procedure,
    )


@app.route("/deleteprocedure/<int:procedure_id>", methods=["POST"])
def delete_procedure(procedure_id):
    procedure = TestProcedure.query.get_or_404(procedure_id)
    db.session.delete(procedure)
    db.session.commit()
    flash("Procedure successfully deleted!", "success")
    return redirect(
        url_for(
            "procedures", procedure_id=procedure_id, project_id=procedure.project_id
        )
    )


# ===== Test Steps ===== #
@app.route("/procedure/<int:procedure_id>")
def procedure(procedure_id):
    current_procedure = TestProcedure.query.get_or_404(procedure_id)

    # All steps that are not setup steps
    procedure_steps = [
        step for step in current_procedure.steps if not step.is_setup_step
    ]

    # Build list of setup steps in this project
    setup_steps = list()
    for step in TestStep.query.filter_by(is_setup_step=True):
        if (
            TestProcedure.query.get(step.procedure_id).project_id
            == current_procedure.project_id
        ):
            setup_steps.append(step)

    setup_steps = get_test_steps_and_results(setup_steps)
    procedure_steps = get_test_steps_and_results(procedure_steps)

    return render_template(
        "teststeps.html",
        title=f"Procedure: {current_procedure.name}",
        procedure=current_procedure,
        test_steps=procedure_steps,
        setup_steps=setup_steps,
    )


# Helper function for procedure route.
# @return A list of tuples mapping steps and results
def get_test_steps_and_results(steps):
    results = []
    for step in steps:
        if len(step.runs) == 0:
            results.append(0)
        else:
            recent_run = max(step.runs, key=lambda x: x.timestamp)
            results.append(1 if recent_run.passing else -1)
    return list(zip(steps, results))


@app.route("/deletestep<int:step_id>", methods=["POST"])
def delete_step(step_id):
    step = TestStep.query.get_or_404(step_id)
    db.session.delete(step)
    db.session.commit()
    flash("Step successfully deleted!", "success")
    return redirect(url_for("procedure", procedure_id=step.procedure_id))


@app.route("/editstep/<step_id>", methods=["GET", "POST"])
def edit_step(step_id):
    editForm = StepForm()
    edit_step = TestStep.query.get_or_404(step_id)
    if editForm.validate_on_submit():
        edit_step.name = editForm.step_name.data
        edit_step.instructions = editForm.instructions.data
        edit_step.pass_condition = editForm.pass_condition.data
        edit_step.is_setup_step = editForm.is_setup_step.data
        db.session.commit()
        flash("Step updated successfully!", "dark")
        return redirect(url_for("procedure", procedure_id=edit_step.procedure_id))
    return render_template(
        "editstep.html", title="Edit Step", editForm=editForm, edit_step=edit_step
    )


@app.route("/procedure/<int:procedure_id>/newstep", methods=["GET", "POST"])
def new_step(procedure_id):
    form = StepForm()
    if form.validate_on_submit():
        step_name = form.step_name.data
        instructions = form.instructions.data
        pass_condition = form.pass_condition.data
        is_setup_step = form.is_setup_step.data
        new_step = TestStep(
            name=step_name,
            procedure_id=procedure_id,
            instructions=instructions,
            pass_condition=pass_condition,
            is_setup_step=is_setup_step,
        )
        db.session.add(new_step)
        db.session.commit()
        return redirect(url_for("procedure", procedure_id=procedure_id))
    return render_template(
        "newstep.html", title="New Step", form=form, procedure_id=procedure_id
    )


@app.route("/procedure/<int:procedure_id>/run", methods=["POST", "GET"])
def run_test_procedure(procedure_id):
    procedure = TestProcedure.query.get_or_404(procedure_id)
    procedure_name = procedure.name

    # Build list of setup steps in this project
    setup_steps = list()
    for step in TestStep.query.filter_by(is_setup_step=True):
        if (
            TestProcedure.query.get(step.procedure_id).project_id
            == procedure.project_id
        ):
            setup_steps.append(step)

    # Run setup steps and then procedure steps
    steps = setup_steps + procedure.steps

    if len(steps) == 0:
        flash("There are currently no test steps to run", "warning")
        return redirect(url_for("procedure", procedure_id=procedure_id))
    form = get_test_run_form(steps)

    if form.is_submitted():
        for field_name, value in form.data.items():
            try:
                step_id = int(field_name)
            except ValueError:
                continue
            if value == "pass":
                new_run = TestRun(step_id=step_id, passing=True)
                db.session.add(new_run)
            elif value == "fail":
                new_run = TestRun(step_id=step_id, passing=False)
                db.session.add(new_run)
        db.session.commit()
        flash("Test run completed", "success")
        return redirect(url_for("procedure", procedure_id=procedure_id))
    return render_template(
        "runtest.html",
        title="Running Test",
        procedure_id=procedure_id,
        form=form,
        steps=steps,
        procedure_name=procedure_name,
    )


@app.before_first_request
def create_tables():
    db.create_all()
