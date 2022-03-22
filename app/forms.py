from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, RadioField
from wtforms.validators import DataRequired


class ProcedureForm(FlaskForm):
    procedure_name = StringField("Procedure Name", validators=[DataRequired()])
    approval = BooleanField("Approval")
    notes = StringField("Notes")
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
    submit = SubmitField("Create Project")
    editSubmit = SubmitField("Save")


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
