from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, FloatField
from wtforms.fields.html5 import DateField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, ValidationError
from ultradb.models import Project, User

def project_query():
    return Project.query

# This should only show active employees...
def user_query():
    return User.query.filter(User.isEmployed == True)

class TimesheetDateRangeForm(FlaskForm):
    startDate = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    endDate = DateField('End Date', validators=[DataRequired()], format='%Y-%m-%d', default=datetime.utcnow())
    submit = SubmitField('Filter timesheets to date range')

class TimesheetForm(FlaskForm):
    user_id = QuerySelectField('Employee Name', query_factory=user_query, allow_blank=True, get_label='username')
    date_of_work = DateField('Date of work. Format in YYYY/MM/DD', validators=[DataRequired()], format='%Y-%m-%d', default=datetime.utcnow())
    project_id = QuerySelectField('Select Project you worked on', query_factory=project_query, allow_blank=True, get_label='name', validators=[DataRequired()])
    hours = FloatField('Hours worked today on selected project')
    comment = StringField('What work did you do')
    update = SubmitField('Update Timesheet Details')
    submit = SubmitField('Add Hours to this Project')

    def validate_hours(self, hours):
        if(hours.data != None):
            if(hours.data < 0.0):
                raise ValidationError('You cannot enter negative hours')
            elif(hours.data > 12):
                raise ValidationError('A maximum of 12 hours can be charged at once')
   
    # Only check the comment field length
    def validate_comment(self, comment):
        if (len(self.comment.data) < 5) or len(self.comment.data) > 200:
            raise ValidationError('Please enter a comment between 5 and 200 characters, unless you did not work today.')
