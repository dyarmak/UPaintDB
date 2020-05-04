from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FloatField, IntegerField
from wtforms.fields.html5 import DateField, URLField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, url
from ultradb.models import (User, Post, Site, Area, Room, 
                            Project, Status, Worktype,
                            Supplier, Brand, Product, Sheen, Paint, Color, PaintColor)


def project_query():
    Project.query

def supplier_query():
    Supplier.query

def brand_query():
    Brand.query

def product_query():
    Product.query

def sheen_query():
    Sheen.query

def color_query():
    Color.query


class NewSupplierForm(FlaskForm):
    name = StringField('Supplier Name', validators=[DataRequired()])
    addr_str = StringField('Address')
    city = StringField('City', validators=[DataRequired()])
    submit = SubmitField('Add new Supplier')

class NewBrandForm(FlaskForm):
    name = StringField('Paint Brand Name, usually same as supplier name', validators=[DataRequired()])
    supplier = QuerySelectField(query_factory= supplier_query, allow_blank=False, validators=[DataRequired()])
    submit = SubmitField('Add new Brand')

class NewProductForm(FlaskForm):
    name = StringField('Product name', validators=[DataRequired()])
    brand = QuerySelectField(query_factory= brand_query, allow_blank=False, validators=[DataRequired()])
    submit = SubmitField('Add new Product')

# In the off chance we need to add a new sheen
# I can add it via the backend
# class NewSheenForm(FlaskForm):
#     name = StringField('Product name')
#     submit = SubmitField('Add new Sheen')

class NewColorForm(FlaskForm):
    name = StringField('Color Name', validators=[DataRequired()])
    code = StringField('Store Color Code. Ex: OC-11, CL-2891')
    submit = SubmitField('Add new Color')

class PaintColorBuilderForm(FlaskForm):
    supplier = QuerySelectField(query_factory= supplier_query, allow_blank=True, validators=[DataRequired()]) # We want this to display the name and city 
    brand = QuerySelectField(query_factory= brand_query, allow_blank=True, get_label='name', validators=[DataRequired()])
    product = QuerySelectField(query_factory= product_query, allow_blank=True, get_label='name', validators=[DataRequired()])
    sheen = QuerySelectField(query_factory= sheen_query, allow_blank=True, get_label='name', validators=[DataRequired()])
    color = QuerySelectField(query_factory= color_query, allow_blank=True, get_label='name', validators=[DataRequired()]) # Would be nice to have code appear aswell
    prod_code = StringField('Product Code')
    base = StringField('Product Base')
    formula = StringField('Formula for this product and base')

    submit = SubmitField('Add new PaintColor')


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    fName = StringField('First Name', validators=[DataRequired, Length(min=2, max=30)])
    lName = StringField('Last Name', validators=[DataRequired, Length(min=2, max=30)])
    cellPhone = StringField('Cell Number', validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    fName = StringField('First Name', validators=[DataRequired(), Length(min=2, max=30)]) # Should DataRaquired have the ()?
    lName = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=30)])
    cellPhone = StringField('Cell Number')
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')


class NewSiteForm(FlaskForm):
    name = StringField('Site Name', validators=[DataRequired()])
    code = StringField('Site Code', validators=[DataRequired()])
    addr_str = StringField('Site Street Address', validators=[DataRequired()])
    city = StringField('Site city', validators=[DataRequired()])
    submit = SubmitField('Post')

def site_query():
    return Site.query

class NewAreaForm(FlaskForm):
    name = StringField('Area Name', validators=[DataRequired()])
    code = StringField('Area Code', validators=[DataRequired()])
    site_id = QuerySelectField(query_factory=site_query, allow_blank=True, get_label='code')
    building = StringField('Building Name', validators=[DataRequired()])
    level = StringField('Floor in Building', validators=[DataRequired()])
    descriptor = StringField('Area Description', validators=[DataRequired()])
    # Need to add this to the the html file
    # color_sheet = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Post') 

class UpdateAreaForm(FlaskForm):
    name = StringField('Area Name', validators=[DataRequired()])
    code = StringField('Area Code', validators=[DataRequired()])
    site_id = QuerySelectField(query_factory=site_query, allow_blank=True, get_label='code')
    building = StringField('Building Name', validators=[DataRequired()])
    level = StringField('Floor in Building', validators=[DataRequired()])
    descriptor = StringField('Area Description', validators=[DataRequired()])
    color_sheet = FileField('Color Sheet', validators=[FileAllowed(['jpg', 'png'])])
    # cs_url = URLField(validators=[url()])
    submit = SubmitField('Update') 

def area_query():
    return Area.query

class NewRoomForm(FlaskForm):
    name = StringField('Room Name or Description', validators=[DataRequired()])
    bm_id = StringField('BM ID if available')
    site_id = QuerySelectField(query_factory=site_query, allow_blank=True)
    area_id = QuerySelectField(query_factory=area_query, allow_blank=True)
    building = StringField('Building name', validators=[Length(max=30)])
    level = IntegerField('Level / Floor of building')
    freq = IntegerField('Frequency of painting in years (Pleae use -1 for As Needed')
    date_last_paint = DateField('Date last painted, Format in YYYY/MM/DD', format='%Y-%m-%d', validators=[Optional()])
    glaccount = StringField('GL Account if avail')
    submit = SubmitField('Post')    


def status_query():
    return Status.query

def type_query():
    return Worktype.query

class NewProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired()])
    site_id = QuerySelectField('Site of Project', query_factory=site_query, allow_blank=True, get_label='code', validators=[DataRequired()])
    status_id = QuerySelectField('Project Status', query_factory=status_query, allow_blank=False, get_label='name', validators=[DataRequired()])
    typeOfWork_id = QuerySelectField('Type of Work',query_factory=type_query, allow_blank=False, get_label='name', validators=[DataRequired()])
    description = StringField('Description of the Job / Scope', validators=[Length(max=250)])
    # Dates should have some validators added!
    date_start = DateField('Start Date. Format in YYYY/MM/DD', format='%Y-%m-%d', validators=[DataRequired()])
    date_finished = DateField('Actual End Date. Format in YYYY/MM/DD', format='%Y-%m-%d', validators=[Optional()])
    target_end_date = DateField('Target End Date. Format in YYYY/MM/DD', format='%Y-%m-%d', validators=[Optional()])
    area_list = QuerySelectMultipleField(query_factory=area_query, get_label='name')
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
    site_id = QuerySelectField('Site of Project', query_factory=site_query, allow_blank=False, get_label='code')
    status_id = QuerySelectField('Project Status', query_factory=status_query, allow_blank=False, get_label='name')
    typeOfWork_id = QuerySelectField('Type of Work',query_factory=type_query, allow_blank=False, get_label='name')
    description = StringField('Description of the Job / Scope', validators=[Length(max=250)])
    # Area and Rooms. I'm not yet sure how to deal with these...
    area_list = QuerySelectMultipleField(query_factory=area_query, get_label='name')
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

def room_query():
    return Room.query

class AreaFilterForm(FlaskForm):
    areas = QuerySelectField('Select an area to filter results by', query_factory=area_query)
    submit = SubmitField('Apply Filter') 

class AddRoomToProjectForm(FlaskForm):
    room_list = QuerySelectMultipleField(query_factory=room_query, get_label='name')
    submit = SubmitField('Add Rooms to Project')  

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
