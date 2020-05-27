from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired
from ultradb.models import Supplier, Brand, Product, Sheen, Paint, Color, PaintColor

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
    code = StringField('Store Color Code. Ex: OC-11 OR CL-2891')
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
