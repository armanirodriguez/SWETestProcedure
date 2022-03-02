from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SelectField, SubmitField, BooleanField, DateTimeField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms.widgets import TextArea
from wtforms.fields import DateField

class procedureForm(FlaskForm):
    formCreatedBy = StringField('Created By',
							validators=[DataRequired(), Length(min=2, max=20)])
    formDateCreated = StringField('Date Created', )
    formProdName = StringField('Name',
							validators=[DataRequired(), Length(min=2, max=20)])
    formRequirements = StringField('Requirements', widget=TextArea())
    formStatus = StringField('Status', validators=[DataRequired()])
    formPriority = SelectField('Priority', choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], validators=[DataRequired()])
    formEstTime = StringField('Est Time', validators=[DataRequired()])
    formVersion = StringField('Version', validators=[DataRequired(), Length(min=1, max=100)])
    formApproval = BooleanField('Approval')
    formNotes = StringField('Notes', widget=TextArea())
    submit = SubmitField('Save')
    cancel = SubmitField('Cancel')

    