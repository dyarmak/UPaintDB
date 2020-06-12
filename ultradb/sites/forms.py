from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, IntegerField
from wtforms.fields.html5 import DateField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Optional
from ultradb.models import Site, Area


def site_query():
    return Site.query

def area_query():
    return Area.query

class NewClientForm(FlaskForm):
    name = StringField('Client / Business Name', validators=[DataRequired()])
    contactName = StringField('Name of Primary Contact Person', validators=[Optional()])
    contactEmail = StringField('Email of Primary Contact Person', validators=[Optional()])
    contactPhone = StringField('Phone number for Primary Contact Person', validators=[Optional()])
    submit = SubmitField('Add Client') 

class UpdateClientForm(FlaskForm):
    name = StringField('Client / Business Name', validators=[DataRequired()])
    contactName = StringField('Name of Primary Contact Person', validators=[Optional()])
    contactEmail = StringField('Email of Primary Contact Person', validators=[Optional()])
    submit = SubmitField('Update Client Info') 

class NewSiteForm(FlaskForm):
    name = StringField('Site Name', validators=[DataRequired()])
    code = StringField('Site Code', validators=[DataRequired()])
    addr_str = StringField('Site Street Address', validators=[DataRequired()])
    city = StringField('Site city', validators=[DataRequired()])
    submit = SubmitField('Add new Site')

class NewAreaForm(FlaskForm):
    name = StringField('Area Name', validators=[DataRequired()])
    code = StringField('Area Code', validators=[DataRequired()])
    site_id = QuerySelectField(query_factory=site_query, allow_blank=True, get_label='code')
    building = StringField('Building Name', validators=[DataRequired()])
    level = StringField('Floor in Building', validators=[DataRequired()])
    descriptor = StringField('Area Description', validators=[DataRequired()])
    # Need to add this to the the html file
    # color_sheet = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Add new Area') 

class UpdateAreaForm(FlaskForm):
    name = StringField('Area Name', validators=[DataRequired()])
    code = StringField('Area Code', validators=[DataRequired()])
    site_id = QuerySelectField(query_factory=site_query, allow_blank=True, get_label='code')
    building = StringField('Building Name', validators=[DataRequired()])
    level = StringField('Floor in Building', validators=[DataRequired()])
    descriptor = StringField('Area Description', validators=[DataRequired()])
    color_sheet = FileField('Color Sheet', validators=[FileAllowed(['jpg', 'png'])])
    # cs_url = URLField(validators=[url()])
    submit = SubmitField('Update Area') 

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
    submit = SubmitField('Add new Room')    