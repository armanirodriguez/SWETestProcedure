from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField,RadioField
from wtforms.validators import DataRequired, Length
from wtforms.widgets import TextArea

class ProcedureForm(FlaskForm):
    procedure_name = StringField('Procedure Name',
							validators=[DataRequired()])
    approval = BooleanField('Approval')
    notes = StringField('Notes', widget=TextArea())
    submit = SubmitField('Save')
    cancel = SubmitField('Cancel')

class StepForm(FlaskForm):
    step_name = StringField('Step Name',
							validators=[DataRequired()])
    instructions = StringField('Test Instructions', widget=TextArea(),validators=[DataRequired()])
    pass_condition = StringField('Pass Condition',validators=[DataRequired()])
    submit = SubmitField('Save')
    cancel = SubmitField('Cancel')

class TestRunFormFactory():
    def __init__(self,test_steps):
        self.test_steps = test_steps
    def get_test_run_form(self):
        # dynamically create test run form
        class TestRunForm(FlaskForm):
            pass

        
        for step in self.test_steps:
            setattr(TestRunForm, str(step.id), RadioField(f"Select the observed result.", choices=[("pass","pass"),("fail","fail")], description="teststep"))
        setattr(TestRunForm,"submit",SubmitField('Save'))
        setattr(TestRunForm,"cancel",SubmitField('Cancel'))
        form = TestRunForm()
        for field in form:
            print(field)
        return TestRunForm()