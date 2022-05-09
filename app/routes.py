from flask import render_template, url_for, flash, redirect, request, session
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db, bcrypt
from app.forms import (
    ChangePasswordForm,
    ProcedureForm,
    StepForm,
    ProjectForm,
    LoginForm,
    UserForm,
    EditProjectForm,
    get_test_run_form,
)
from app.models import TestProcedure, TestStep, Project, TestRun, Version, User
from app.util import ensure_procedure, ensure_version, get_test_steps_and_results


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title="Home Page")


# ===== Projects ===== #

# Display all projects
@app.route("/projects", methods=["GET", "POST"])
@login_required
def projects():
    form = ProjectForm()
    if form.validate_on_submit():
        if not current_user.permissions & User.PERM_EDIT:
            flash("Permission denied", "danger")
            return redirect(url_for("projects"))
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


# Endpoint for deleting projects
@app.route("/deleteproject/<int:project_id>", methods=["POST"])
@login_required
def delete_project(project_id):
    if not current_user.permissions & User.PERM_EDIT:
        flash("Permission denied", "danger")
        return redirect(url_for("projects"))
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash("Project successfully deleted!", "success")
    return redirect(url_for("projects"))


# Endpoint for editing projects
@app.route("/editproject/<int:project_id>", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    if not current_user.permissions & User.PERM_EDIT:
        flash("Permission denied", "danger")
        return redirect(url_for("projects"))
    editForm = EditProjectForm()
    project = Project.query.get_or_404(project_id)
    if editForm.validate_on_submit():
        project.name = editForm.project_name.data
        db.session.commit()
    return redirect(url_for("projects"))


# Endpoint for adding a project version
@app.route("/newversion/<int:project_id>", methods=["POST"])
@login_required
def new_version(project_id):
    if not current_user.permissions & User.PERM_EDIT:
        flash("Permission denied", "danger")
        return redirect(request.referrer)
    name = request.form.get("version_name")
    if any(x.name == name for x in Version.query.filter_by(project_id=project_id)):
        flash("Version already exists", "warning")
    else:
        new_version = Version(project_id=project_id, name=name)
        db.session.add(new_version)
        db.session.commit()
        flash("New version has been added.", "success")
    return redirect(request.referrer)


# ===== Test Procedures ===== #

# Display all procedures within a project
@app.route("/project/<int:project_id>/procedures")
@login_required
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


# Form to create a new procedure.
@app.route("/project/<int:project_id>/newprocedure", methods=["GET", "POST"])
@login_required
def new_procedure(project_id):
    form = ProcedureForm()
    if form.validate_on_submit():
        procedure_name = form.procedure_name.data
        notes = form.notes.data
        myData = TestProcedure(
            name=procedure_name, notes=notes, project_id=project_id, approval=False
        )
        db.session.add(myData)
        db.session.commit()

        flash(f"Procedure {procedure_name} created successfully!", "success")

        return redirect(url_for("procedures", project_id=project_id))
    return render_template(
        "newprocedure.html", title="New Procedure", form=form, project_id=project_id
    )


# Form to edit an existing procedure
@app.route("/editprocedure/<procedure_id>", methods=["GET", "POST"])
@login_required
def edit_procedure(procedure_id):
    editForm = ProcedureForm()
    edit_procedure = TestProcedure.query.get_or_404(procedure_id)
    if editForm.validate_on_submit():
        edit_procedure.name = editForm.procedure_name.data
        edit_procedure.notes = editForm.notes.data
        db.session.commit()
        flash(f"Procedure {editForm.procedure_name.data} updated!", "dark")
        return redirect(url_for("procedures", project_id=edit_procedure.project_id))
    return render_template(
        "editprocedure.html",
        title="Edit Procedure",
        editForm=editForm,
        edit_procedure=edit_procedure,
    )


# Endpoint to delete a procedure
@app.route("/deleteprocedure/<int:procedure_id>", methods=["POST"])
@login_required
def delete_procedure(procedure_id):
    if not current_user.permissions & User.PERM_EDIT:
        flash("Permission denied", "danger")
    else:
        procedure = TestProcedure.query.get_or_404(procedure_id)
        db.session.delete(procedure)
        db.session.commit()
        flash("Procedure successfully deleted!", "success")
    return redirect(
        url_for(
            "procedures", procedure_id=procedure_id, project_id=procedure.project_id
        )
    )


@app.route("/approveprocedure/<int:procedure_id>", methods=["POST"])
@login_required
def approve_procedure(procedure_id):
    if not current_user.permissions & User.PERM_ADMIN:
        flash("Permission denied", "danger")
        return redirect(url_for("home"))
    procedure = TestProcedure.query.get_or_404(procedure_id)
    if request.form.get("deny.x") is not None:
        procedure.approval = False
    else:
        procedure.approval = True
    procedure.approvalNotes = request.form.get("notes")
    if request.form.get("notes") == "":
        procedure.approvalNotes = "Denied"
    db.session.commit()
    return redirect(url_for("admin"))


# ===== Test Steps ===== #

# Display all steps within procedure
@app.route("/procedure/<int:procedure_id>")
@login_required
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


# Endpoint to delete a step.
@app.route("/deletestep<int:step_id>", methods=["POST"])
@login_required
def delete_step(step_id):
    if not current_user.permissions & User.PERM_EDIT:
        flash("Permission denied", "danger")
    else:
        step = TestStep.query.get_or_404(step_id)
        db.session.delete(step)
        db.session.commit()
        flash("Step successfully deleted!", "success")
    return redirect(url_for("procedure", procedure_id=step.procedure_id))


# Form to edit an existing step.
@app.route("/editstep/<step_id>", methods=["GET", "POST"])
@login_required
def edit_step(step_id):
    editForm = StepForm()
    edit_step = TestStep.query.get_or_404(step_id)
    if not current_user.permissions & User.PERM_EDIT:
        flash("Permission denied", "danger")
        return redirect(url_for("procedure", procedure_id=edit_step.procedure_id))
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


# Form to create a new step
@app.route("/procedure/<int:procedure_id>/newstep", methods=["GET", "POST"])
@login_required
def new_step(procedure_id):
    if not current_user.permissions & User.PERM_EDIT:
        flash("Permission denied", "danger")
        return redirect(url_for("procedure", procedure_id=procedure_id))
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


# Generates a form to run all tests within a procedure
@app.route("/procedure/<int:procedure_id>/run", methods=["POST", "GET"])
@login_required
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


# Change the current displayed project version
@app.route("/editcurrentversion/<int:project_id>/<version_name>", methods=["GET"])
@login_required
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


# Change the procedure_id session variable (for dashboard)
@app.route("/editcurrentprocedure/<int:project_id>/<procedure_name>", methods=["GET"])
def edit_current_procedure(project_id, procedure_name):
    curr_project = Project.query.get(project_id)
    if curr_project is None:
        return redirect(request.referrer)
    new_procedure = next(
        (p for p in curr_project.procedures if p.name == procedure_name), None
    )
    if new_procedure is None:
        return redirect(request.referrer)
    session["procedure_id"] = new_procedure.id

    return redirect(request.referrer)


# Dashboard
@app.route("/dashboard/<int:project_id>", methods=["GET", "POST"])
def dashboard(project_id):
    current_project = Project.query.get_or_404(project_id)
    ensure_version(project_id)
    if len(current_project.procedures) == 0:
        return redirect(request.referrer)
    ensure_procedure(project_id)

    procedure_steps = [
        step
        for x in current_project.procedures
        for step in x.steps
        if not step.is_setup_step
    ]

    # Build list of setup steps in this project
    setup_steps = list()
    for step in TestStep.query.filter_by(is_setup_step=True):
        if TestProcedure.query.get(step.procedure_id).project_id == current_project.id:
            setup_steps.append(step)
    setup_steps_clean = setup_steps  # Pre-Mapping
    procedure_steps_clean = procedure_steps  # Pre-Mapping
    setup_steps = get_test_steps_and_results(setup_steps, session["version_id"])
    procedure_steps = get_test_steps_and_results(procedure_steps, session["version_id"])
    steps = setup_steps + procedure_steps

    stepsPassing = []
    stepsFailing = []
    stepsPending = []
    passingValues = []
    for step, value in steps:
        passingValues.append(value)
        if value == 0:
            stepsPending.append(step)
        elif value == 1:
            stepsPassing.append(step)
        elif value == -1:
            stepsFailing.append(step)

    # GRAPH 1 - PIE CHART DATA
    passingValues = [
        passingValues.count(-1),
        passingValues.count(1),
        passingValues.count(0),
    ]  # R, G, O

    # X AXIS LABELS OF GRAPH 2
    versions = []
    for version in current_project.versions:
        versions.append(version.name)

    # GRAPH 2 - LINE GRAPH DATA
    percent_passing_list = [0] * len(current_project.versions)
    i = 0
    for version in current_project.versions:
        totalSteps = 0
        curr_version_setup_steps = get_test_steps_and_results(
            setup_steps_clean, version.id
        )
        curr_version_procedure_steps = get_test_steps_and_results(
            procedure_steps_clean, version.id
        )
        curr_version_steps = curr_version_setup_steps + curr_version_procedure_steps
        for step, value in curr_version_steps:
            if value == 1:
                percent_passing_list[i] += 1
            totalSteps += 1
        i += 1
    if totalSteps != 0:
        percent_passing_list = [(x * 100) / totalSteps for x in percent_passing_list]

    # GRAPH 3 - PROGRESS BAR DATA
    progressValues = []
    current_procedure = TestProcedure.query.get(session.get("procedure_id"))
    current_steps = [step for step in current_procedure.steps if not step.is_setup_step]
    current_steps = get_test_steps_and_results(current_steps, session["version_id"])
    progress_steps = setup_steps + current_steps
    for step, value in progress_steps:
        progressValues.append(value)
    progressValues = [
        progressValues.count(-1),
        progressValues.count(1),
        progressValues.count(0),
    ]  # R, G, O

    return render_template(
        "dashboard.html",
        current_project=current_project,
        project_id=project_id,
        current_version_name=Version.query.get(session.get("version_id")).name,
        current_procedure_name=current_procedure.name,
        versions=versions,
        passingValues=passingValues,
        progressValues=progressValues,
        percent_passing_list=percent_passing_list,
        setup_steps=setup_steps,
        procedure_steps=procedure_steps,
        steps=steps,
        stepsPassing=stepsPassing,
        stepsFailing=stepsFailing,
        stepsPending=stepsPending,
    )


# === Users === #
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"Welcome, {form.username.data}!", "success")
            if current_user.force_password_change:
                flash("Please change your password before continuing.", "warning")
                return redirect(url_for("change_password"))
            next_route = request.args.get("next")
            return redirect(next_route) if next_route else redirect(url_for("home"))
        else:
            flash("Could not log in. Please check your credentials.", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for("home"))


@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        password = form.new_password.data
        confirm = form.confirm_password.data
        if password != confirm:
            flash("Passwords do not match.", "danger")
        else:
            current_user.password = bcrypt.generate_password_hash(password).decode(
                "UTF-8"
            )
            if current_user.force_password_change:
                current_user.force_password_change = False
            db.session.commit()
            flash("Password has been changed.", "success")
        return redirect(url_for("home"))
    return render_template("changepassword.html", form=form, title="Change Password")


@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    if not current_user.permissions & User.PERM_ADMIN:
        flash("Permission denied", "danger")
        if request.referrer is not None:
            return redirect(request.referrer)
        return redirect(url_for("home"))
    user_form = UserForm()
    if user_form.validate_on_submit():
        username = user_form.username.data
        password = user_form.password.data
        confirm = user_form.confirm_password.data
        perm_admin = user_form.perm_admin.data
        perm_edit = user_form.perm_edit.data
        permissions = 0
        if perm_admin:
            permissions |= User.PERM_ADMIN
        if perm_edit:
            permissions |= User.PERM_EDIT
        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template(
                "admin.html", title="Admin Panel", user_form=user_form
            )
        elif (
            User.query.first() is not None
            and User.query.first().username.lower() == username.lower()
        ):
            flash("Username taken. Please choose a different one.", "danger")
        else:
            new_user = User(
                username=username,
                password=bcrypt.generate_password_hash(password).decode("UTF-8"),
                permissions=permissions,
            )
            db.session.add(new_user)
            db.session.commit()
            flash("User has been added", "success")

    unapproved_steps = [
        x
        for x in TestProcedure.query.filter_by(approval=False)
        if x.approvalNotes is None or len(x.approvalNotes) == 0
    ]
    return render_template(
        "admin.html",
        title="Admin Panel",
        user_form=user_form,
        unapproved=unapproved_steps,
    )


# Creates tables for database. #
@app.before_first_request
def create_tables():
    db.create_all()
    if len(User.query.all()) == 0:
        default_user = User(
            username="admin",
            password=bcrypt.generate_password_hash("admin").decode("UTF-8"),
            permissions=User.PERM_ADMIN | User.PERM_EDIT,
            force_password_change=True,
        )
        db.session.add(default_user)
        db.session.commit()
