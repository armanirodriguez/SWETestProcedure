from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SelectField, SubmitField, BooleanField, DateTimeField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms.widgets import TextArea
from wtforms.fields import DateField

class procedureForm(FlaskForm):
    formProcedureName = StringField('Procedure Name',
							validators=[DataRequired(), Length(min=2, max=20)])
    formApproval = BooleanField('Approval')
    formNotes = StringField('Notes', widget=TextArea())
    submit = SubmitField('Save')
    cancel = SubmitField('Cancel')

class stepForm(FlaskForm):
    step_name = StringField('Step Name',
							validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Save')
    cancel = SubmitField('Cancel')

    