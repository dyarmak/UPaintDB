# Run this after deleting the site.db database

from datetime import datetime

# Create a new instance of the DB
from ultradb import app, db
db.drop_all()
db.create_all()
print("Created a new db")

# Add an admin account
from ultradb.models import User
from ultradb import bcrypt
pw_hash = bcrypt.generate_password_hash('Mountain99').decode('UTF-8')
admin = User(username='Admin', email='dyarmak@gmail.com', password=pw_hash, fName='Dan', lName='Yarmak', cellPhone='2502150536')
db.session.add(admin)
db.session.commit()
print("Admin account added to db.")

# Add an account for steve
pw_hash = bcrypt.generate_password_hash('Bossman').decode('UTF-8')
steve = User(username='SteveY', email='ultrapainting@shaw.ca', password=pw_hash, fName='Steve', lName='Yarmak', cellPhone='2507185047')
db.session.add(steve)
db.session.commit()
print("SteveY account added to db.")

# Add an account for Russ
pw_hash = bcrypt.generate_password_hash('RussWideman').decode('UTF-8')
russ = User(username='RussW', email='russ.wideman@yahoo.com', password=pw_hash, fName='Russ', lName='Wideman', cellPhone='2504702588')
db.session.add(russ)
db.session.commit()
print("RussW account added to db.")

# Add an Account for Chris
pw_hash = bcrypt.generate_password_hash('ChrisLowen').decode('UTF-8')
chris = User(username='ChrisL', email='chrislowen@hotmail.com', password=pw_hash, fName='Chris', lName='Lowen', cellPhone='2508995132')
db.session.add(chris)
db.session.commit()
print("ChrisL account added to db.")


# Add a post so it doesn't crash. Maybe instead change the route to a 404 error?
from ultradb.models import Post

#################################################################
################ Update Logs ####################################
#################################################################

TODO = Post(user_id=admin.id,
                title='Planned Future Features',
                date_posted= datetime.utcnow(), 
                content='''
Links:
- Add links to the Add New ____ paint related items on the "Add New Paint" Page

Image Hosting and Serving:
- Set up an AWS S3 account to store and host uploaded files.
-- Add pdf and image upload interface for a project
-- Add paintCanLid image uploading for a PaintColor (adds nice redundancy)

Timesheets:                
- Interface to charge time to a project
--- With weekly (On Monday) report of hours worked by employees

PaintColors:
- Model for PaintColor Association table for Areas and Rooms
- Interface for attributing PaintColors with Areas, Rooms, and Projects.

- Search Functionality
--- Room by BM_ID
--- Area? (fuzzymatch) - Not sure this would be better than browsing for it?

- List ordering buttons for Areas, Rooms, Projects. 
--- Buttons for date newest/oldest, active projects (area/room list of active projects?)

''')

V01 = Post(user_id=admin.id,
                title='Update: V 0.1',
                date_posted= datetime.strptime('20190415', '%Y%m%d'), 
                content='''
Initial release has:
Capability to 
1) Add a Blog style Post, likely to be removed later? Unless usefull.
-- Would like to add photos to a post.
1) Add information about Sites, Area, Rooms, and associate them together
2) Browse existing Sites, Areas, Rooms in a structured hierarchy.
-- A Room belongs to an Area, which belongs to a Site.
-- EX: Area 2West is in site KGH
3) Upload and view the color sheet for a particular area.
-- need to add PaintColor object association to areas/rooms.
''')

V02 = Post(user_id=admin.id,
                title='Update: V 0.2', 
                date_posted= datetime.strptime('20190520', '%Y%m%d'), 
                content='''
First update adds:
1) Project DB models and forms for interface

2) Projects Interface.
-- Create a new Project, defining its name, type, status, scope, 
-- Timesheets will later be associated to a given Project.

3) Better handling of Area Colorsheets.
-- Uploads are store locally, and will be deleted daily until it is changed to upload to an AWS S3 bucket.
''')


V03 = Post(user_id=admin.id,
                title='New Version Update: V 0.3', 
                date_posted= datetime.strptime('20190628', '%Y%m%d'), 
                content='''
With this update I've added: 
1) The Paint Builder interface.
--- After logging in, the side Navigation bar (bottom on mobile) now has an option to "Add a New Paint". 
2) Area Filters for adding a room to a Project.
3) No-reload filtering for the paint builder (will add to the Add Room / Area to Project page )
4) Models, interface and html for New: 
- Suppliers
- Brands
- Products
- Colors
- NOT for Sheen
--- Still need to add links to these on the New Paint Page
''')

db.session.add(TODO)
db.session.add(V01)
db.session.add(V02)
db.session.add(V03)
db.session.commit()

print("Added a Update Logs")


# Add some sites
from ultradb.models import Site
kgh = Site(name='Kelowna General Hospital', code='KGH', addr_str='2268 Pandosy Street', city='Kelowna')
vjh = Site(name='Vernon Jubilee Hospital', code='VJH', addr_str='2101 32 Street', city='Vernon')
dlj = Site(name='David Lloyd Jone', code='DLJ', addr_str='934 Bernard Avenue', city='Kelowna')
ctw = Site(name='Cottonwoods Care Centre', code='CTW', addr_str='2255 Ethel Street', city='Kelowna')
polext = Site(name='Polson Extended Care Unit', code='PolEXT', addr_str='2102 32 Street', city='Vernon')
db.session.add(kgh)
db.session.add(vjh)
db.session.add(dlj)
db.session.add(ctw)
db.session.add(polext)
db.session.commit()
print("Added KGH, VJH, DLJ, CTW, PolExt")


# Add some areas
from ultradb.models import Area
# These areas are from the KGH Rooms list
RPOT = Area(name='Rehab/Physio/OT', code='A1', site_id=kgh.id, building='Abbott', level=1)
CAC1 = Area(name='CAC 1st Floor', code='CAC1', site_id=kgh.id, building='UBC-CAC', level=1)
CAC2 = Area(name='CAC 2nd Floor', code='CAC2', site_id=kgh.id, building='UBC-CAC', level=2)
Parkade = Area(name='Parkade', code='Parkade', site_id=kgh.id, building='UBC-CAC', level=-1)
Royal1 = Area(name='Royal 1st Floor', code='R1', site_id=kgh.id, building='Royal', level=1)
Royal2 = Area(name='Royal 2nd Floor', code='R2', site_id=kgh.id, building='Royal', level=2)
Royal4 = Area(name='Royal 4th Floor', code='R4', site_id=kgh.id, building='Royal', level=3)
Royal5 = Area(name='Royal 5th Floor', code='R5', site_id=kgh.id, building='Royal', level=4)
Strath1 = Area(name='Strathcona 1st Floor', code='S1', site_id=kgh.id, building='Stratcona', level=1)
Strath2 = Area(name='Strathcona 2nd Floor', code='S2', site_id=kgh.id, building='Stratcona', level=2)
Strath3 = Area(name='Strathcona 3rd Floor', code='S3', site_id=kgh.id, building='Stratcona', level=3)
Strath4 = Area(name='Strathcona 4th Floor', code='S4', site_id=kgh.id, building='Stratcona', level=4)
Strath5 = Area(name='Strathcona 5th Floor', code='S5', site_id=kgh.id, building='Stratcona', level=5)
Cent1 = Area(name='Centennial 1st Floor', code='C1', site_id=kgh.id, building='Centennial', level=1)
Cent2 = Area(name='Centennial 2nd Floor', code='C2', site_id=kgh.id, building='Centennial', level=2)
Cent3 = Area(name='Centennial 3rd Floor', code='C3', site_id=kgh.id, building='Centennial', level=3)
Cent4 = Area(name='Centennial 4th Floor', code='C4', site_id=kgh.id, building='Centennial', level=4)
Cent5 = Area(name='Centennial 5th Floor', code='C5', site_id=kgh.id, building='Centennial', level=5)
Cent6 = Area(name='Centennial 6th Floor', code='C6', site_id=kgh.id, building='Centennial', level=6)
KGHOther = Area(name='KGH-Other', code='KGH-Other', site_id=kgh.id, building='KGH-Other', level=0)
cardCath = Area(name='Cardiac/Cath', code='Cardiac', site_id=kgh.id, building='Royal', level=1)
kgh_ccsi_1 = Area(name='Cancer Clinic 1st Floor', code='KCCSI1', site_id=kgh.id, building='CCSI', level='1', descriptor="Main floor of CCSI Kelowna")
kgh_ccsi_2 = Area(name='Cancer Clinic 2nd Floor', code='KCCSI2', site_id=kgh.id, building='CCSI', level='2', descriptor="Second floor of CCSI Kelowna")
SS1 = Area(name='Support Services 1st Floor', code='SS1', site_id=kgh.id, building='Support Services', level=1)
SS2 = Area(name='Support Services 2nd Floor', code='SS2', site_id=kgh.id, building='Support Services', level=2)

db.session.add(RPOT)
db.session.add(CAC1)
db.session.add(CAC2)
db.session.add(Parkade)
db.session.add(Royal1)
db.session.add(Royal2)
db.session.add(Royal4)
db.session.add(Royal5)
db.session.add(Strath1)
db.session.add(Strath2)
db.session.add(Strath3)
db.session.add(Strath4)
db.session.add(Strath5)
db.session.add(Cent1)
db.session.add(Cent2)
db.session.add(Cent3)
db.session.add(Cent4)
db.session.add(Cent5)
db.session.add(Cent6)
db.session.add(KGHOther)
db.session.add(cardCath)
db.session.add(kgh_ccsi_1)
db.session.add(kgh_ccsi_2)
db.session.add(SS1)
db.session.add(SS2)

print('Added all building and level combos for KGH as Areas')

# These areas are from the VJH Rooms list

P1 = Area(name='Polson Extended', code='PolExt', site_id=polext.id, building='Polson Extended Care', level=1)
P2 = Area(name='Polson Extended Upper rooms', code='PolExt2', site_id=polext.id, building='Polson Extended Care', level=2)
HN0 = Area(name='Hospital North 0th Floor', code='HN0', site_id=vjh.id, building='North Tower', level=0)
HN1 = Area(name='Hospital North 1st Floor', code='HN1', site_id=vjh.id, building='North Tower', level=1)
HN2 = Area(name='Hospital North 2nd Floor', code='HN2', site_id=vjh.id, building='North Tower', level=2)
HN3 = Area(name='Hospital North 3rd Floor', code='HN3', site_id=vjh.id, building='North Tower', level=3)
HN4 = Area(name='Hospital North 4th Floor', code='HN4', site_id=vjh.id, building='North Tower', level=4)
HS0 = Area(name='Hospital South 0th Floor', code='HS0', site_id=vjh.id, building='South Tower', level=0)
HS1 = Area(name='Hospital South 1st Floor', code='HS1', site_id=vjh.id, building='South Tower', level=1)
HS2 = Area(name='Hospital South 2nd Floor', code='HS2', site_id=vjh.id, building='South Tower', level=2)
HS3 = Area(name='Hospital South 3rd Floor', code='HS3', site_id=vjh.id, building='South Tower', level=3)
VJHOther = Area(name='VJH-Other', code='VJH-Other', site_id=vjh.id, building='VJH Other ', level=0)

db.session.add(P1)
db.session.add(P2) 
db.session.add(HN0)
db.session.add(HN1)
db.session.add(HN2)
db.session.add(HN3)
db.session.add(HN4)
db.session.add(HS0)
db.session.add(HS1)
db.session.add(HS2)
db.session.add(HS3)
db.session.add(VJHOther)

print('Added all building and level combos for VJH as Areas')

# Add additional KGH Areas
pros = Area(name='Orthotics/ Prosthetics Clinic', code='ORTHO', site_id=kgh.id, building='Abbott', level='1', descriptor="Across the hall from the Rehab pool")
ot = Area(name='Occupational Therapy', code='OT', site_id=kgh.id, building='Abbott', level='1', descriptor="Right turn past MS clinic")

# Add additional VJH Areas
vjhmh = Area(name='Mental Health / Psychiatry', code='VJH-MH', site_id=vjh.id, building='Jubilee', level='1', descriptor="Straight down hall from South entrance")
vjhwext = Area(name='Western Exterior', code='VJH-WExt', site_id=vjh.id, building='South and North Exterior', level='1', descriptor="Walls just outside West entrance near CCSI")

db.session.add(pros)
db.session.add(ot)
db.session.add(vjhmh)
db.session.add(vjhwext)
db.session.commit()
print("Added Prosthetics, Occupational Therapy, VJH Western Exterior, and VJH Mental Health")


#**************************************# 
#*********** Add some rooms ***********# 
#**************************************# 

import pandas as pd
import sqlite3
from sqlalchemy import create_engine

# Here we can grab KGH rooms from the excel file
path_to_kghexcel = r'C:\Users\dyarmak\Dropbox\Sharing with Phone\UltraDB\PythonCode\RoomLists\KGH-Sorted.xlsx'
kghdf = pd.read_excel(path_to_kghexcel, index_col=0)
path_to_db = r'C:\Users\dyarmak\Dropbox\Sharing with Phone\UltraDB\PythonCode\UltraDBSite\site.db'

# Create your connection.
cnx = sqlite3.connect(path_to_db)
# Lets start with areas, then do sites
areas = pd.read_sql_query("SELECT * FROM Area", cnx)
sites = pd.read_sql_query("SELECT * FROM Site", cnx)

# Grab just the columns we need
areas = areas[['id','name']]
areas.rename({'id':'area_id'}, axis=1, inplace=True)

# Grab just the columns we need
sites = sites[['id','code']]
sites.rename({'id':'site_id'}, axis=1, inplace=True)

kgh_with_areas = pd.merge(kghdf, areas, how='left', left_on='area', right_on='name')
kgh_with_site_and_areas = pd.merge(kgh_with_areas, sites, how='left', left_on='site', right_on='code')
kgh_with_site_and_areas.drop(['code', 'name_y', 'site','area'], axis=1, inplace=True)
kgh_with_site_and_areas.rename({'name_x':'name'}, axis=1, inplace = True)

kgh_for_insert = kgh_with_site_and_areas[['bm_id', 'name', 'location', 'date_last_paint', 'freq', 'date_next_paint', 'site_id', 'area_id', 'GLACCOUNT']]
kgh_for_insert = kgh_for_insert.set_index('bm_id')

engine = create_engine(r'sqlite:///C:\Users\dyarmak\Dropbox\Sharing with Phone\UltraDB\PythonCode\UltraDBSite\site.db', echo=False)
kgh_for_insert.to_sql(name='room', con=engine, if_exists='append')

print('KGH Rooms added with area_id')

# Now we do the same for VJH
# I've broken our Polson Extended and linked those rooms to the PolExt Site.
path_to_vjhexcel = r'C:\Users\dyarmak\Dropbox\Sharing with Phone\UltraDB\PythonCode\RoomLists\VJH-Sorted.xlsx'
vjhdf = pd.read_excel(path_to_vjhexcel, index_col=0)

# Create connection.
cnx = sqlite3.connect(path_to_db)
# Lets start with areas, then do sites
areas = pd.read_sql_query("SELECT * FROM Area", cnx)
sites = pd.read_sql_query("SELECT * FROM Site", cnx)

# Grab just the columns we need from areas
areas = areas[['id','name', 'code']]
areas.rename({'id':'area_id'}, axis=1, inplace=True)

vjh_with_areas = pd.merge(vjhdf, areas, how='left', left_on='area', right_on='code')

# Grab just the columns we need sites
sites = sites[['id','code']]
sites.rename({'id':'site_id'}, axis=1, inplace=True)

vjh_with_site_and_areas = pd.merge(vjh_with_areas, sites, how='left', left_on='site', right_on='code')

DBCols = ['bm_id', 'name', 'location', 'date_last_paint', 'freq', 'date_next_paint', 'site_id', 'area_id', 'GLACCOUNT']

# Get PolExt by itself
polExt = vjh_with_site_and_areas.loc[vjh_with_site_and_areas.area.isin(['PolExt', 'PolExt2'])]

polExt = polExt.drop(['code_x','code_y','name_y', 'site','area'], axis=1)
polExt = polExt.rename({'name_x':'name'}, axis=1)
polExt_for_insert = polExt[DBCols]
polExt_for_insert = polExt_for_insert.set_index('bm_id')

# Get VJH without PolExt
vjh_no_PolExt = vjh_with_site_and_areas.loc[~vjh_with_site_and_areas.area.isin(['PolExt', 'PolExt2'])].copy()
vjh_no_PolExt.drop(['code_x', 'code_y', 'name_y', 'site','area'], axis=1, inplace=True)
vjh_no_PolExt.rename({'name_x':'name'}, axis=1, inplace = True)
vjh_for_insert = vjh_no_PolExt[DBCols]
vjh_for_insert = vjh_for_insert.set_index('bm_id')

vjh_for_insert.to_sql(name='room', con=engine, if_exists='append')
polExt_for_insert.to_sql(name='room', con=engine, if_exists='append')

print('VJH Rooms added with area_id')


# we can also add rooms this way...
# I'd like to change these to something more like...
# query for bm_id, then change the area_id to the new area... hmmm
from ultradb.models import Room

# Lets update the areas that these rooms are associated with
# Going forward, I can create a list of rooms for each area. For now we have Prosthetics and Occupational Therapy
pros_rm_list = ["A1-016", "A1-035", "A1-041", "A1-042", "A1-035A", "A1-034", "A1-040", "A1-039", "A1-037"]
ot_rm_list=["A1-021"]

# for whatever reason this one isn't already in the Data Set.
pr2 = Room(bm_id="A1-035", name='Fitting Room 1', area_id=pros.id, site_id=kgh.id) 
db.session.add(pr2)
db.session.commit()

# Set the area for prosthetics
for rm in pros_rm_list:
    print(rm)
    rm_obj = Room.query.filter_by(bm_id=rm).first()
    try:
        rm_obj.area_id = pros.id
        db.session.add(rm_obj)
    except AttributeError:
        pass

# set the area for Ocupational Therapy
for rm in ot_rm_list:
    rm_obj = Room.query.filter_by(bm_id=rm).first()
    try:
        rm_obj.area_id = pros.id
        db.session.add(rm_obj)
    except AttributeError:
        pass

db.session.commit()



# pr1 = Room(bm_id="A1-016", name='Washroom in Prosthetics', area_id=pros.id, site_id=kgh.id)

# pr3 = Room(bm_id="A1-041", name='Office in Reception', area_id=pros.id, site_id=kgh.id) 
# pr4 = Room(bm_id="A1-042", name='Reception Desk', area_id=pros.id, site_id=kgh.id) 
# pr5 = Room(bm_id="A1-035A", name='Fitting Room 2', area_id=pros.id, site_id=kgh.id)
# pr6 = Room(bm_id="A1-034", name='Hallway - Orthotics/Prosthetics', area_id=pros.id, site_id=kgh.id) 
# pr7 = Room(bm_id="A1-040", name='Fitting Room 3', area_id=pros.id, site_id=kgh.id) 
# pr8 = Room(bm_id="A1-039", name='Plater and Casting Room', area_id=pros.id, site_id=kgh.id)   
# pr9 = Room(bm_id="A1-037", name='Washroom in Prosthetics', area_id=pros.id, site_id=kgh.id) 
# pr10 = Room(bm_id="A1-021", name='Washroom outside OT Reception', area_id=ot.id, site_id=kgh.id) 

# db.session.add(pr1)

# db.session.add(pr3)
# db.session.add(pr4)
# db.session.add(pr5)
# db.session.add(pr6)
# db.session.add(pr7)
# db.session.add(pr8)
# db.session.add(pr9)
# db.session.add(pr10)
# db.session.commit()

print("Associated Pros/Ortho rooms with Pros/Ortho Area")


# Lets add some ColorSheets
from ultradb.models import ColorSheet

# Vernon ColorSheets
    # Hospital North
cs_HN0 = ColorSheet(area_id=HN0.id, name="HN0-2020-02-24-e4.jpg", date_uploaded=datetime.strptime('2020-02-24','%Y-%m-%d'))
cs_HN1 = ColorSheet(area_id=HN1.id, name="HN1-2020-02-24-6e.jpg", date_uploaded=datetime.strptime('2020-02-24','%Y-%m-%d'))
cs_HN11 = ColorSheet(area_id=HN1.id, name="HN1-2020-02-24-72.jpg", date_uploaded=datetime.strptime('2020-02-24','%Y-%m-%d'))
cs_HN12 = ColorSheet(area_id=HN1.id, name="HN1-2020-02-24-e0.jpg", date_uploaded=datetime.strptime('2020-02-24','%Y-%m-%d'))
cs_HN2 = ColorSheet(area_id=HN2.id, name="HN2-2020-02-24-31.jpg", date_uploaded=datetime.strptime('2020-02-24','%Y-%m-%d'))
cs_HN21 = ColorSheet(area_id=HN2.id, name="HN2-2020-02-24-d7.jpg", date_uploaded=datetime.strptime('2020-02-24','%Y-%m-%d'))
cs_HN3 = ColorSheet(area_id=HN3.id, name="HN3-2020-02-24-1d.jpg", date_uploaded=datetime.strptime('2020-02-24','%Y-%m-%d'))
cs_HN4 = ColorSheet(area_id=HN4.id, name="HN4-2020-02-24-b5.jpg", date_uploaded=datetime.strptime('2020-02-24','%Y-%m-%d'))
cs_VJH_MH = ColorSheet(area_id=vjhmh.id, name="VJH-MH-2020-02-24-b5.jpg", date_uploaded=datetime.strptime('2020-02-24','%Y-%m-%d'))
cs_VJH_MH2 = ColorSheet(area_id=vjhmh.id, name="VJH-MH-2020-02-24-e9.jpg", date_uploaded=datetime.strptime('2020-02-24','%Y-%m-%d'))

db.session.add(cs_HN0)
db.session.add(cs_HN1)
db.session.add(cs_HN11)
db.session.add(cs_HN12)
db.session.add(cs_HN2)
db.session.add(cs_HN21)
db.session.add(cs_HN3)
db.session.add(cs_HN4)
db.session.add(cs_VJH_MH)
db.session.add(cs_VJH_MH2)


db.session.commit()

print("Added some ColorSheets")

# Example of how to build the area locations string
# a = Area.query.filter_by(id=1).first()
# area_site_code = Site.query.filter_by(id=a.site_id).first().code
# print(f"Area'{a.code}' is located at site '{area_site_code}'")

# Add some Statuses
from ultradb.models import Status

st1 = Status(name = 'New/Upcoming', description = 'Upcoming, unquoted work')
st2 = Status(name = 'Quoted', description = 'Quote has been sent')
st3 = Status(name = 'InProgress', description = 'Project has begun')
st4 = Status(name = 'PaintingComplete', description = 'Painting has been completed. Waiting on billing')
st5 = Status(name = 'Invoiced', description = 'Invoice has been sent, awaiting payment')
st6 = Status(name = 'Paused', description = 'Project on Pause for some reason, will resume later')
st7 = Status(name = 'Cancelled', description = 'Project Was Cancelled, will not be resuming')

db.session.add(st1)
db.session.add(st2)
db.session.add(st3)
db.session.add(st4)
db.session.add(st5)
db.session.add(st6)
db.session.add(st7)

db.session.commit()
print('Added some Statuses')

# Add some Project Types
from ultradb.models import Worktype

tp1 = Worktype(code = 'SM', name = 'Scheduled Maintenance', description = 'Scheduled Maintenance Painting')
tp2 = Worktype(code = 'AN', name = 'As Needed', description = 'As needed Painting')
tp3 = Worktype(code = 'CT', name = 'Contract', description = 'Painting done on a contract Basis. Hours for costing only')
tp4 = Worktype(code = 'WR', name = 'Warranty', description = 'Warranty work.')


db.session.add(tp1)
db.session.add(tp2)
db.session.add(tp3)
db.session.add(tp4)

db.session.commit()

print('Added some Types')


# Add Project
from ultradb.models import Project

# kgh = Site.query.filter_by(code='KGH').first() 
# # If I was adding this elsewhere I would need to query each item going in.

pr1 = Project(name = 'Prosthetics 2019 repaint', site_id=kgh.id, status_id=st5.id , typeOfWork_id=tp3.id)
pr2 = Project(name = '2West 2019 repaint', site_id=kgh.id, status_id=st3.id , typeOfWork_id=tp1.id)
pr3 = Project(name = 'VJH MRI', site_id=vjh.id, status_id=st3.id , typeOfWork_id=tp3.id, quote_amt=18000 )
pr4 = Project(name = 'VJH 2020 Kitchen Repaint', site_id=vjh.id, status_id=st5.id, typeOfWork_id=tp1.id)

db.session.add(pr1)
db.session.add(pr2)
db.session.add(pr3)
db.session.add(pr4)

db.session.commit()

    # Many to many operations
        # obj = Model.query.filter_by(criteria).first()
        # proj.room_list.append(obj) OR
        # proj.room_list.remove(obj) 

print("Added some Projects")

# Add some Suppliers
from ultradb.models import Supplier

s1 = Supplier(name='Dulux Paints', addr_str= '1856 Spall Rd', city='Kelowna')
s2 = Supplier(name='Sherwin Williams', addr_str= '1990 Cooper Rd', city='Kelowna')
s3 = Supplier(name='Cloverdale Paint', addr_str= '1950B Springfield Rd', city='Kelowna')
s4 = Supplier(name='Cloverdale Paint', addr_str= '2804 44 Ave', city='Vernon')
s5 = Supplier(name='Dulux Paints', addr_str= '4309 27 St', city='Vernon')

db.session.add(s1)
db.session.add(s2)
db.session.add(s3)
db.session.add(s4)
db.session.add(s5)

db.session.commit()
print('Added some Suppliers')

# Add some Brands
from ultradb.models import Brand

b1 = Brand(name='Dulux', supplier_id=s1.id)
b2 = Brand(name='Sherwin Williams', supplier_id=s2.id)
b3 = Brand(name='Cloverdale', supplier_id=s3.id)

db.session.add(b1)
db.session.add(b2)
db.session.add(b3)

db.session.commit()
print('Added some Brands')

# Add some Products
from ultradb.models import Product

p1 = Product(name='Lifemaster', brand_id=b1.id)
p2 = Product(name='Diamond', brand_id=b1.id)
p3 = Product(name='ProMar 200 Zero VOC Interior Latex', brand_id=b2.id)
p4 = Product(name='Eco Logic', brand_id=b3.id)

db.session.add(p1)
db.session.add(p2)
db.session.add(p3)
db.session.add(p4)

db.session.commit()
print('Added some Products')

# Add some Sheens
from ultradb.models import Sheen

sh1 = Sheen(name='Flat')
sh2 = Sheen(name='Eggshell')
sh3 = Sheen(name='Pearl')
sh4 = Sheen(name='Low-Gloss')
sh5 = Sheen(name='Semi-Gloss')
sh6 = Sheen(name='Gloss')
sh7 = Sheen(name='High-Gloss')
sh8 = Sheen(name='Matt')

db.session.add(sh1)
db.session.add(sh2)
db.session.add(sh3)
db.session.add(sh4)
db.session.add(sh5)
db.session.add(sh6)
db.session.add(sh7)
db.session.add(sh8)

db.session.commit()
print('Added some Sheens')

# Add some Paints
from ultradb.models import Paint

pt1 = Paint(supplier_id=s1.id , brand_id=b1.id, 
            product_id=p2.id , sheen_id=sh3.id)
pt2 = Paint(supplier_id=s2.id , brand_id=b2.id, 
            product_id=p3.id , sheen_id=sh5.id)
pt3 = Paint(supplier_id=s1.id , brand_id=b1.id, 
            product_id=p1.id , sheen_id=sh2.id)


db.session.add(pt1)
db.session.add(pt2)
db.session.add(pt3)

db.session.commit()
print('Added some Paints')

# Add some Colors
from ultradb.models import Color

c1 = Color(name="Water Chestnut")
c2 = Color(name="Star Thirstle")
c3 = Color(name="Falcon")
c4 = Color(name="Clay Beige", code='OC-11')

db.session.add(c1)
db.session.add(c2)
db.session.add(c3)
db.session.add(c4)

db.session.commit()
print('Added some Colors')

# Add some PaintColors
from ultradb.models import PaintColor

pc1 = PaintColor(paint_id= pt1.id, color_id= c1.id)
pc2 = PaintColor(paint_id= pt2.id, color_id= c2.id)
pc3 = PaintColor(paint_id= pt3.id, color_id= c4.id, prod_code='59311', base='59311 WHITE')

db.session.add(pc1)
db.session.add(pc2)
db.session.add(pc3)

db.session.commit()
print('Added some PaintColors')

# Add some timesheet entries
from ultradb.models import Timesheet
dt = datetime.utcnow()

dts1 = Timesheet(dateOfWork=datetime.strptime('2019-06-17', "%Y-%m-%d"), dateSubmit=dt, user_id=admin.id, project_id=pr1.id, hours=6.0, comment='Dans first test timsheet entry', isNotWorkDay=False, completed=True)
dts2 = Timesheet(dateOfWork=datetime.strptime('2019-06-18', "%Y-%m-%d"), dateSubmit=dt, user_id=admin.id, project_id=pr1.id, hours=2.0, comment='Dans second test timsheet entry', isNotWorkDay=False, completed=True)
dts3 = Timesheet(dateOfWork=datetime.strptime('2019-06-19', "%Y-%m-%d"), dateSubmit=dt, user_id=admin.id, project_id=pr2.id, hours=4.5, comment='Dans third test timsheet entry', isNotWorkDay=False, completed=True)
dts4 = Timesheet(dateOfWork=datetime.strptime('2019-06-20', "%Y-%m-%d"), dateSubmit=dt, user_id=admin.id, project_id=pr1.id, hours=2.5, comment='Dans fourth test timsheet entry', isNotWorkDay=False, completed=True)
dts5 = Timesheet(dateOfWork=datetime.strptime('2019-06-21', "%Y-%m-%d"), dateSubmit=dt, user_id=admin.id, project_id=pr3.id, hours=5.5, comment='Sealed and first coated walls', isNotWorkDay=False, completed=True)


sts1 = Timesheet(dateOfWork=datetime.strptime('2019-06-17', "%Y-%m-%d"), dateSubmit=dt, user_id=steve.id, project_id=pr1.id, hours=8.0, comment='Steves first test timsheet entry', isNotWorkDay=False, completed=True)
sts2 = Timesheet(dateOfWork=datetime.strptime('2019-06-18', "%Y-%m-%d"), dateSubmit=dt, user_id=steve.id, project_id=pr2.id, hours=6.5, comment='Steves second test timsheet entry', isNotWorkDay=False, completed=True)
sts3 = Timesheet(dateOfWork=datetime.strptime('2019-06-19', "%Y-%m-%d"), dateSubmit=dt, user_id=steve.id, project_id=pr1.id, hours=5.5, comment='Steves third test timsheet entry', isNotWorkDay=False, completed=True)
sts4 = Timesheet(dateOfWork=datetime.strptime('2019-06-20', "%Y-%m-%d"), dateSubmit=dt, user_id=steve.id, project_id=pr1.id, hours=7.5, comment='Steves fourth test timsheet entry', isNotWorkDay=False, completed=True)
sts5 = Timesheet(dateOfWork=datetime.strptime('2019-06-21', "%Y-%m-%d"), dateSubmit=dt, user_id=steve.id, project_id=pr3.id, hours=4.0, comment='Sanded walls, primed door frames, couble coated tops for T-Bar install', isNotWorkDay=False, completed=True)


db.session.add(dts1)
db.session.add(dts2)
db.session.add(dts3)
db.session.add(dts4)
db.session.add(dts5)

db.session.add(sts1)
db.session.add(sts2)
db.session.add(sts3)
db.session.add(sts4)
db.session.add(sts5)

db.session.commit()

# Create the many-to-many relationship user-timesheet
dts1.user.append(admin)
dts2.user.append(admin)
dts3.user.append(admin)
dts4.user.append(admin)
dts5.user.append(admin)

sts1.user.append(steve)
sts2.user.append(steve)
sts3.user.append(steve)
sts4.user.append(steve)
sts5.user.append(steve)

# Create the many-to-many relationship project-timesheet
dts1.project.append(pr1)
dts2.project.append(pr1)
dts3.project.append(pr2)
dts4.project.append(pr1)
dts5.project.append(pr3)

sts1.project.append(pr1)
sts2.project.append(pr1)
sts3.project.append(pr2)
sts4.project.append(pr1)
sts5.project.append(pr3)


db.session.commit()
print('Added some timesheet entries')
