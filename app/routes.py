# Maps the site URLs to a specific function that will handle the logic for that URL.#

from flask import render_template, url_for, flash, redirect, request, session

from app import db
from app import app
from app.forms import ProcedureForm, StepForm, ProjectForm, get_test_run_form
from app.models import TestProcedure, TestStep, Project, TestRun, Version
from app.util import ensure_version, get_test_steps_and_results


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title="Home Page")


# ===== Projects ===== #

# Form to store and create a new procedure. #

@app.route("/projects", methods=["GET", "POST"])
def projects():
    form = ProjectForm()
    if form.validate_on_submit():
        new_project = Project(name=form.project_name.data)
        db.session.add(new_project)
        db.session.commit()

        init_version = Version(
            name=form.initial_version_name.data, project_id=new_project.id
        )
        db.session.add(init_version)
        db.session.commit()

        return redirect(url_for("projects"))
    projects = Project.query.all()
    return render_template(
        "projects.html", title="projects", form=form, projects=projects
    )

# Form to delete a project. #

@app.route("/deleteproject/<int:project_id>", methods=["POST"])
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash("Project successfully deleted!", "success")
    return redirect(url_for("projects"))

# Form to edit a project. #

@app.route("/editproject/<int:project_id>", methods=["GET", "POST"])
def edit_project(project_id):
    editForm = ProjectForm()
    project = Project.query.get_or_404(project_id)
    print(editForm.project_name.data)
    if editForm.validate_on_submit():
        project.name = editForm.project_name.data
        db.session.commit()
    return redirect(url_for("projects"))


# Form to create a new version of a project. #

@app.route("/newversion/<int:project_id>", methods=["POST"])
def new_version(project_id):
    name = request.form.get("version_name")
    if any(x.name == name for x in Version.query.filter_by(project_id=project_id)):
        flash("Version already exists", "warning")
    new_version = Version(project_id=project_id, name=name)
    db.session.add(new_version)
    db.session.commit()
    flash("New version has been added.", "success")
    return redirect(request.referrer)


# ===== Test Procedures ===== #

# Form to store procedures. #

@app.route("/project/<int:project_id>/procedures")
def procedures(project_id):
    ensure_version(project_id)
    current_project = Project.query.get_or_404(project_id)
    procedures = current_project.procedures
    return render_template(
        "procedures.html",
        title="Procedure",
        procedures=procedures,
        project_id=project_id,
        current_project=current_project,
        current_version_name=Version.query.get(session.get("version_id")).name,
    )

# Form to create a new procedure. #

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

# Form to edit an existing procedure. #

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

# Form to delete a procedure. #

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

# Sets current procedure, and then create setup steps. #

@app.route("/procedure/<int:procedure_id>")
def procedure(procedure_id):
    current_procedure = TestProcedure.query.get_or_404(procedure_id)
    current_project = Project.query.get_or_404(current_procedure.project_id)

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

    setup_steps = get_test_steps_and_results(setup_steps, session["version_id"])
    procedure_steps = get_test_steps_and_results(procedure_steps, session["version_id"])

    return render_template(
        "teststeps.html",
        title=f"Procedure: {current_procedure.name}",
        procedure=current_procedure,
        test_steps=procedure_steps,
        setup_steps=setup_steps,
        current_project=current_project,
        current_version_name=Version.query.get(session.get("version_id")).name,
    )

# Form to delete a step. #

@app.route("/deletestep<int:step_id>", methods=["POST"])
def delete_step(step_id):
    step = TestStep.query.get_or_404(step_id)
    db.session.delete(step)
    db.session.commit()
    flash("Step successfully deleted!", "success")
    return redirect(url_for("procedure", procedure_id=step.procedure_id))

# Form to edit an existing step. #

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

# Form to create a new step. #

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

# Form for running a test procedure. #

@app.route("/procedure/<int:procedure_id>/run", methods=["POST", "GET"])
def run_test_procedure(procedure_id):
    procedure = TestProcedure.query.get_or_404(procedure_id)
    ensure_version(procedure.project_id)
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
    steps = setup_steps + [x for x in procedure.steps if not x.is_setup_step]

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
                new_run = TestRun(
                    step_id=step_id, passing=True, version_id=session["version_id"]
                )
                db.session.add(new_run)
            elif value == "fail":
                new_run = TestRun(
                    step_id=step_id, passing=False, version_id=session["version_id"]
                )
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

# Form to edit the version of a project. #

@app.route("/editcurrentversion/<int:project_id>/<version_name>", methods=["GET"])
def edit_current_version(project_id, version_name):
    curr_project = Project.query.get(project_id)
    if curr_project is None:
        return redirect(request.referrer)
    new_version = next(
        (v for v in curr_project.versions if v.name == version_name), None
    )
    if new_version is None:
        return redirect(request.referrer)
    session["version_id"] = new_version.id
    return redirect(request.referrer)

# Creates tables for database. #

@app.before_first_request
def create_tables():
    db.create_all()
