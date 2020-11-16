from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, BooleanField
from wtforms.fields.html5 import DateField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import DataRequired, Length, Optional
from ultradb.models import Site, Area, Room, Status, Worktype, Client

def client_query():
    return Client.query

def status_query():
    return Status.query

def type_query():
    return Worktype.query

def site_query():
    return Site.query

def area_query():
    return Area.query

def room_query():
    return Room.query

class FilterProjectsForm(FlaskForm):
    client_id = QuerySelectField('Client Name', query_factory=client_query, allow_blank=True, get_label='name')
    site_id = QuerySelectField('Site of Project', query_factory=site_query, allow_blank=True, get_label='code')
    status_id = QuerySelectField('Status of Project', query_factory=status_query, allow_blank=True, get_label='name')
    typeOfWork_id = QuerySelectField('Type of Work',query_factory=type_query, allow_blank=True, get_label='name')
    start_date_after = DateField('Projects with Start Date After', format='%Y-%m-%d', validators=[Optional()])
    start_date_before = DateField('Projects with Start Date Before', format='%Y-%m-%d', validators=[Optional()])
    finish_date_after = DateField('Projects with Finish Date After', format='%Y-%m-%d', validators=[Optional()])
    finish_date_before = DateField('Projects with Finish Date Before', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Apply Filters')  

class NewProjectSimpleForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired()])
    client_id = QuerySelectField('Client', query_factory=client_query, allow_blank=True, get_label='name', validators=[DataRequired()])
    site_id = QuerySelectField('Site of Project', query_factory=site_query, allow_blank=True, get_label='code', validators=[DataRequired()])
    status_id = QuerySelectField('Project Status', query_factory=status_query, allow_blank=False, get_label='name', validators=[DataRequired()])
    typeOfWork_id = QuerySelectField('Type of Work',query_factory=type_query, allow_blank=False, get_label='name', validators=[DataRequired()])
    description = StringField('Description of the Job / Scope', validators=[Length(max=250)])
    # Dates should have some validators added!
    date_start = DateField('Start Date. Format in YYYY/MM/DD', format='%Y-%m-%d', validators=[DataRequired()])
    damage_comment = StringField('Describe damage level', validators=[Length(max=500), Optional()])
    extenuating_circumstances = StringField('Describe any extenuating circumstances', validators=[Length(max=500), Optional()])
    submit = SubmitField('Create Project')  


class NewProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired()])
    client_id = QuerySelectField('Client', query_factory=client_query, allow_blank=True, get_label='name', validators=[DataRequired()])
    site_id = QuerySelectField('Site of Project', query_factory=site_query, allow_blank=True, get_label='code', validators=[DataRequired()])
    status_id = QuerySelectField('Project Status', query_factory=status_query, allow_blank=False, get_label='name', validators=[DataRequired()])
    typeOfWork_id = QuerySelectField('Type of Work',query_factory=type_query, allow_blank=False, get_label='name', validators=[DataRequired()])
    description = StringField('Description of the Job / Scope', validators=[Length(max=250)])
    # Dates should have some validators added!
    date_start = DateField('Start Date. Format in YYYY/MM/DD', format='%Y-%m-%d', validators=[DataRequired()])
    date_finished = DateField('Actual End Date. Format in YYYY/MM/DD', format='%Y-%m-%d', validators=[Optional()])
    target_end_date = DateField('Target End Date. Format in YYYY/MM/DD', format='%Y-%m-%d', validators=[Optional()])
    # area_list = QuerySelectMultipleField(query_factory=area_query, get_label='name')
    hours_estimate = FloatField('Number of man-hours to complete', validators=[Optional()])
    quote_amt = FloatField('If contract, Quoted amount', validators=[Optional()])
    invoice_amt = FloatField('If completed, Invoiced amount', validators=[Optional()])
    labour = FloatField('If completed, Actual Hours worked', validators=[Optional()])
    materials = FloatField('If completed, Actual Materials Used', validators=[Optional()])
    damage_comment = StringField('Describe damage level', validators=[Length(max=500), Optional()])
    extenuating_circumstances = StringField('Describe any extenuating circumstances', validators=[Length(max=500), Optional()])
    submit = SubmitField('Create Project')  

class UpdateProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired()])
    client_id = QuerySelectField('Client', query_factory=client_query, allow_blank=True, get_label='name', validators=[DataRequired()])
    site_id = QuerySelectField('Site of Project', query_factory=site_query, allow_blank=False, get_label='code')
    status_id = QuerySelectField('Project Status', query_factory=status_query, allow_blank=False, get_label='name')
    typeOfWork_id = QuerySelectField('Type of Work',query_factory=type_query, allow_blank=False, get_label='name')
    description = StringField('Description of the Job / Scope', validators=[Length(max=250)])
    # Area and Rooms. I'm not yet sure how to deal with these...
    # area_list = QuerySelectMultipleField(query_factory=area_query, get_label='name')
    # room_list = 
    # Dates should have some validators added!
    date_start = DateField('Start Date. Format in YYYY/MM/DD', validators=[DataRequired()], format='%Y-%m-%d')
    date_finished = DateField('Actual End Date. Format in YYYY/MM/DD', format='%Y-%m-%d', validators=[Optional()])
    target_end_date = DateField('Target End Date. Format in YYYY/MM/DD', format='%Y-%m-%d', validators=[Optional()])
    hours_estimate = FloatField('Number of man-hours to complete', validators=[Optional()])
    quote_amt = FloatField('If contract, Quoted amount', validators=[Optional()])
    invoice_amt = FloatField('If completed, Invoiced amount', validators=[Optional()])
    labour = FloatField('If completed, Actual Hours worked', validators=[Optional()])
    materials = FloatField('If completed, Actual Materials Used', validators=[Optional()])
    damage_comment = StringField('Describe damage level', validators=[Length(max=500), Optional()])
    extenuating_circumstances = StringField('Describe any extenuating circumstances', validators=[Length(max=500), Optional()])
    submit = SubmitField('Update Project')  

class AreaFilterForm(FlaskForm):
    areas = QuerySelectField('Select an area to filter results by', query_factory=area_query)
    submit = SubmitField('Apply Filter') 

class AddRoomToProjectForm(FlaskForm):
    room_list = QuerySelectMultipleField(query_factory=room_query, get_label='name')
    submit = SubmitField('Update Room List')  