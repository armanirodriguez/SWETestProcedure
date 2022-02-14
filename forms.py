from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class procedureForm(FlaskForm):
    name = StringField('Name',
							validators=[DataRequired(), Length(min=2, max=20)])
    version = StringField('Version', validators=[DataRequired(), Length(min=3, max=3)])
    approval = BooleanField('Approval')
    notes = StringField('Notes')
    submit = SubmitField('Save')
    cancel = SubmitField('Cancel')