from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, FloatField
from wtforms.fields.html5 import DateField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, ValidationError
from ultradb.models import Project

def project_query():
    Project.query

class TimesheetDateRangeForm(FlaskForm):
    startDate = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    endDate = DateField('End Date', validators=[DataRequired()], format='%Y-%m-%d', default=datetime.utcnow())
    submit = SubmitField('Filter timesheets to date range')

class TimesheetForm(FlaskForm):
    dateOfWork = DateField('Date of work. Format in YYYY/MM/DD', validators=[DataRequired()], format='%Y-%m-%d', default=datetime.utcnow())
    project_id = QuerySelectField('Select Project you worked on', query_factory=project_query, get_label='name')
    hours = FloatField('Hours worked today on selected project')
    comment = StringField('What work did you do')
    isNotWorkDay = BooleanField('Non-work day', default=False)
    completed = BooleanField('All hour for this day?', default=False)
    submit = SubmitField('Add Hours to this Project')

    def validate_hours(self, hours):
        if(hours.data != None):
            if(hours.data < 0.0):
                raise ValidationError('You cannot enter negative hours')
            elif(hours.data > 12):
                raise ValidationError('A maximum of 12 hours can be charged at once')

    # Check that if hours == 0, check isNotWorkDay box
    def validate_isNotWorkDay(self, isNotWorkDay):
        if(self.isNotWorkDay.data == False and self.hours.data <= 0):
            raise ValidationError('If you did not work today, please check the Box')
    
    # Only check the comment field length if isNotWorkDay == False
    def validate_comment(self, comment):
        if (self.isNotWorkDay.data == False):
            if (len(self.comment.data) < 5) or len(self.comment.data) > 200:
                raise ValidationError('Please enter a comment between 5 and 200 characters, unless you did not work today.')
