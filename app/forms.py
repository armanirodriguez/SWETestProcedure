# Integrates forms into Flask app, and creates a set form for each aspect of testing.#

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField
from wtforms.validators import DataRequired, EqualTo


class ProcedureForm(FlaskForm):
    procedure_name = StringField("Procedure Name", validators=[DataRequired()])
    notes = StringField("Description")
    submit = SubmitField("Save")


class StepForm(FlaskForm):
    step_name = StringField("Step Name", validators=[DataRequired()])
    instructions = StringField("Test Instructions", validators=[DataRequired()])
    pass_condition = StringField("Pass Condition", validators=[DataRequired()])
    is_setup_step = BooleanField(
        "Is this a setup step? (Will be applied to all procedures)"
    )
    submit = SubmitField("Save")


class ProjectForm(FlaskForm):
    project_name = StringField("Project Name", validators=[DataRequired()])
    initial_version_name = StringField("Initial Version", validators=[DataRequired()])
    submit = SubmitField("Create Project")
    editSubmit = SubmitField("Save")


class EditProjectForm(FlaskForm):
    project_name = StringField("Project Name", validators=[DataRequired()])
    submit = SubmitField("Create Project")
    editSubmit = SubmitField("Save")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class UserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            EqualTo("confirm_password", message="Passwords must match"),
        ],
    )
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    perm_admin = BooleanField("Admin access")
    perm_edit = BooleanField("Can Edit")
    submit = SubmitField("Create User")


class ChangePasswordForm(FlaskForm):
    new_password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            EqualTo("confirm_password", message="Passwords must match."),
        ],
    )
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Change Password")


def get_test_run_form(steps):
    # dynamically create test run form
    class TestRunForm(FlaskForm):
        pass

    for step in steps:
        setattr(
            TestRunForm,
            str(step.id),
            RadioField(
                "Select the observed result.",
                choices=[("pass", "pass"), ("fail", "fail")],
                description="teststep",
            ),
        )
    setattr(TestRunForm, "submit", SubmitField("Save Results"))
    return TestRunForm()
