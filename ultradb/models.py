from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, flash, redirect, url_for
from sqlalchemy.orm import relationship
from ultradb import db, login_manager
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint


# Login Manager functions 
@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.query.get(int(user_id))
    return None

@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to view that page.', 'warning')
    return redirect(url_for('auth_bp.login'))


# UserTimesheet many-to-many table
user_timesheet = db.Table('user_timesheet',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('timesheet_id', db.Integer, db.ForeignKey('timesheet.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    fName = db.Column(db.String(30), nullable=False)
    lName = db.Column(db.String(30), nullable=False)
    cellPhone = db.Column(db.String(20))
    image_file = db.Column(db.String(40), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    timesheets = db.relationship('Timesheet', secondary=user_timesheet, backref=db.backref('user', lazy='dynamic'), lazy='dynamic')
    isEmployed = db.Column(db.Boolean, default=True)
    access_level = db.Column(db.Integer, nullable=False, default=1)
    # I need to define different user access profiles, which defines who can see what pages.
    # There is a flask add on for this (UserRole)
    # level 7 is admin and you see everything.
    # level 5 is manager, you see everything
    # level 3 is employee, you view but not update projects
    # level 1 is outside user, no hours access. 
    # access_profile = db.Column(db.Integer)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"



# Define a Client, mostly just for job filtering puposes
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    contactName = db.Column(db.String(50))
    contactEmail = db.Column(db.String(50), unique=True)
    contactPhone = db.Column(db.String(50))
    projects = db.relationship('Project', backref='client', lazy=True)
    # clientcontacts = relationship('ClientContact')
    # companyEmail = db.Column(db.String(50))

    # billingAddress = db.Column(db.String(50))

    def __repr__(self):
        return f"Client(id={self.id}, name='{self.name}')"


# Realizing that what we really want is a client contacts list
#   
# class ClientContact(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
#     name = db.Column(db.String(50), unique=True, nullable=False)
#     contactName = db.Column(db.String(50))
#     contactEmail = db.Column(db.String(50), unique=True)
#     contactPhone = db.Column(db.String(50))

# Defines a timesheet entry
class Timesheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dateOfWork = db.Column(db.Date, nullable=False)
    dateSubmit = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    hours = db.Column(db.Float, nullable=False, default=0)
    isNotWorkDay = db.Column(db.Boolean) # Mon-Fri = False, Sat and Sun = True
    comment = db.Column(db.String(200))
    completed = db.Column(db.Boolean) # Flag for a completed work day

    def __repr__(self):
        return f"Timesheet('{self.id}', '{self.user_id}', '{self.project_id}')"

# Need some way to track completed work days...
# class WorkDay(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     date = db.Column(db.Date, nullable=False)
#     completed = db.Column(db.Boolean) # Flag for a completed work day

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

# Define model for a physical job site
class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), nullable=False)
    addr_str = db.Column(db.String(100))
    city = db.Column(db.String(100), nullable=False)
    projects = db.relationship('Project', backref='site', lazy=True)
    areas = db.relationship('Area', backref='site', lazy=True)

    def __repr__(self):
        return f"Site('{self.code}', '{self.name}' in '{self.city}')"

# Defines an are within a site
class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), nullable=False)
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'),
                          nullable=False)
    building = db.Column(db.String(100), nullable=False) # should probably have no default
    level = db.Column(db.String(2), nullable=False) # should probably have no default
    descriptor = db.Column(db.Text)
    color_sheets = db.relationship('ColorSheet', backref='color', lazy=True)
    color_sheet = db.Column(db.String(40), nullable=False, default='default_color_sheet.jpg')
    rooms = db.relationship('Room', backref='area', lazy=True)

    def __repr__(self):
        return f"<Area '{self.name} - {self.code}>"


class ColorSheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=False)
    name = db.Column(db.String(40), nullable=False, default='default_color_sheet.jpg')
    date_uploaded = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"ColorSheet('{self.area_id}', '{self.name}')"


# Defines a room within an area
class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bm_id = db.Column(db.String(25))
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(50))
    description = db.Column(db.String(100))
    # Create a column called orig_paint_date and give it the same values as date_last_paint
    # need to do this in the migration script
    orig_paint_date = db.Column(db.DateTime)
    # date_last_paint will only store the date of the most recent paint job. 
    date_last_paint = db.Column(db.DateTime)

    freq = db.Column(db.Integer)
    date_next_paint = db.Column(db.DateTime)
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'),
                          nullable=False)
    # We get this information through the relationship with area
    # building = db.Column(db.String(30))
    # level = db.Column(db.Integer)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'),
                          nullable=False)
    glaccount = db.Column(db.String(50))

    def __repr__(self):
        return f"Room('{self.bm_id}', '{self.name}', '{self.site_id},' '{self.area_id}')"


# Defines a type of project
class Worktype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    description = db.Column(db.String(150)) 
    projects = db.relationship('Project', backref='worktype', lazy=True)

    def __repr__(self):
        return f"WorkType('{self.id}', '{self.name}', '{self.code}')"

# Defines status of project
class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(150), nullable=False)
    projects = db.relationship('Project', backref='status', lazy=True)

    def __repr__(self):
        return f"Status('{self.id}', '{self.name}', '{self.description}')"

# ProjectArea many-to-many table
project_area = db.Table('project_area',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('area_id', db.Integer, db.ForeignKey('area.id'), primary_key=True)
)

# ProjectRoom many-to-many table
project_room = db.Table('project_room',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('room_id', db.Integer, db.ForeignKey('room.id'), primary_key=True)
)

# ProjectTimesheet many-to-many table
project_timesheet = db.Table('project_timesheet',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('timesheet_id', db.Integer, db.ForeignKey('timesheet.id'), primary_key=True) 
)

# Defines a Project
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'))
    area_list = db.relationship('Area', secondary=project_area, backref=db.backref('projects', lazy='dynamic'), lazy='dynamic') # Project can have many areas
    room_list = db.relationship('Room', secondary=project_room, backref=db.backref('projects', lazy='dynamic'), lazy='dynamic') # Project can have many Rooms
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    typeOfWork_id = db.Column(db.Integer, db.ForeignKey('worktype.id'))
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(250))
    date_start = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_finished = db.Column(db.DateTime)
    target_end_date = db.Column(db.DateTime)
    hours_estimate = db.Column(db.Float)
    # curr_hours_actual = Sum(timesheet WHERE timesheet.project_id = project.id )
    quote_amt = db.Column(db.Float)
    invoice_amt = db.Column(db.Float)
    labour = db.Column(db.Float)
    materials = db.Column(db.Float)
    # damage_level = relationship to DamageClass?
    damage_comment = db.Column(db.String(500))
    extenuating_circumstances = db.Column(db.String(500))
    timesheets = db.relationship('Timesheet', secondary=project_timesheet, backref=db.backref('project', lazy='dynamic'), lazy='dynamic')
    purchase_order = db.Column(db.String(50)) # for invoicing
    work_order = db.Column(db.String(50)) # 
    # bm_proj_id = db.Column(db.String(50)) # Email subject line info for tracking 


    def __repr__(self):
        return f"Project('{self.id}', '{self.name}', '{self.site_id}')"

# Paint or other Supplier
class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    addr_str = db.Column(db.String(100))
    city = db.Column(db.String(100), nullable=False)
    brands = db.relationship('Brand', backref='supplier', lazy='dynamic')
    paints = db.relationship('Paint', backref='supplier', lazy='dynamic')

    def __repr__(self):
        return f"Supplier('{self.id}', '{self.name}', '{self.city}')"

    def __str__(self):
        return f"{self.name} in {self.city}"

class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    products = db.relationship('Product', backref='brand')
    paints = db.relationship('Paint', backref='brand')
    
    def __repr__(self):
        return f"Brand('{self.id}', '{self.name}', '{self.supplier_id}')"

    def __str__(self):
        return f"{self.name}"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'))
    paints = db.relationship('Paint', backref='product', lazy='dynamic')

    def __repr__(self):
        return f"Product('{self.id}', '{self.name}', '{self.brand_id}')"

class Sheen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    paints = db.relationship('Paint', backref='sheen', lazy='dynamic')

    def __repr__(self):
        return f"Sheen('{self.id}', '{self.name}')"
    
class Paint(db.Model):
    __table_args__ = tuple(UniqueConstraint('supplier_id', 'brand_id', 'product_id', 'sheen_id', name='_paint_uc'))
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)    
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    sheen_id = db.Column(db.Integer, db.ForeignKey('sheen.id'), nullable=False)
    paintcolors = db.relationship('PaintColor', backref='paint', lazy='dynamic')

    def __repr__(self):
        return f"Paint('{self.id}', '{self.supplier_id}', '{self.brand_id}', '{self.product_id}', '{self.sheen_id}')"

# Example name=Falcon, code=2834D 
class Color(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    code = db.Column(db.String(15))
    paintcolors = db.relationship('PaintColor', backref='color', lazy='dynamic')
    
    def __repr__(self):
        return f"Color('{self.id}', '{self.name}')"

# Example prod_code=59311 , base=59311 WHITE, formula= CX-2,BX-10
class PaintColor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paint_id = db.Column(db.Integer, db.ForeignKey('paint.id'), nullable=False)
    color_id = db.Column(db.Integer, db.ForeignKey('color.id'), nullable=False)
    prod_code = db.Column(db.String(15))
    base = db.Column(db.String(15))
    formula = db.Column(db.String(100))

    def __repr__(self):
        return f"PaintColor('{self.id}', '{self.paint_id}', '{self.color_id}')"

