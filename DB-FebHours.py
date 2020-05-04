# This script is intended to be run to add hours to the DB

# In a sense this is a backup of the hours for the month of Feb

from datetime import datetime
from ultradb import app, db
from ultradb.models import User, Site, Status, Worktype

# Grab todays date
dt = datetime.utcnow()

# Grab User accounts
steve = User.query.filter_by(username='SteveY').first()
russ = User.query.filter_by(username='RussW').first()
chris = User.query.filter_by(username='ChrisL').first()
dan = User.query.filter_by(username='Admin').first()

# Grab Sites
kgh = Site.query.filter_by(code='KGH').first()
vjh = Site.query.filter_by(code='VJH').first()
polext = Site.query.filter_by(code='PolEXT').first()

# Grab Status
stat_inProg = Status.query.filter_by(name='InProgress').first()
stat_complete = Status.query.filter_by(name='PaintingComplete').first()

# Grab WorkTypes
SM = Worktype.query.filter_by(code='SM').first()
CT = Worktype.query.filter_by(code='CT').first()

# Create Projects
from ultradb.models import Project

vjhMedRec = Project(name='VJH Medical Records Winter 2020', site_id=vjh.id, status_id=stat_inProg.id, typeOfWork_id=SM.id,
                    description='Repaint of Medical Records', date_start=datetime.strptime('2020-01-27', '%Y-%m-%d'),
                    target_end_date=datetime.strptime('2020-02-22', '%Y-%m-%d'))

KGHPaintSchedule = Project(name='KGH Painting Schedule Update', site_id=kgh.id, status_id=stat_inProg.id, typeOfWork_id=SM.id,
                    description='Met with Craig to plan upcoming work', date_start=datetime.strptime('2020-02-07', '%Y-%m-%d'))

PolExtWinter2020 = Project(name='Polson Extended Winter 2020', site_id=polext.id, status_id=stat_inProg.id, typeOfWork_id=SM.id,
                    description='Painting some Tub Rooms in Polson Extended', date_start=datetime.strptime('2020-02-09', '%Y-%m-%d'))

AWARooms = Project(name='AWA Rooms A2-201 and A2-211', site_id=vjh.id, status_id=stat_inProg.id, typeOfWork_id=SM.id,
                    description='Painting 2 rooms in the AWA', date_start=datetime.strptime('2020-01-27', '%Y-%m-%d'))

Gamma2 = Project(name='Gamma Camera #2', site_id=vjh.id, status_id=stat_inProg.id, typeOfWork_id=CT.id,
                    description='Painting the Gamma Camera room', date_start=datetime.strptime('2020-02-27', '%Y-%m-%d'))

CancerStaffRoom = Project(name='Cancer Center Staff Room', site_id=vjh.id, status_id=stat_inProg.id, typeOfWork_id=SM.id,
                    description='Painting the Gamma Camera room', date_start=datetime.strptime('2020-02-27', '%Y-%m-%d'))

StrathChapel = Project(name = 'Strathcona Chapel', site_id=kgh.id, status_id=stat_complete.id, typeOfWork_id=CT.id, 
                description = 'Double prime wood walls, paint all walls and ceilings', quote_amt=2200, 
                purchase_order='12345', work_order='67890', date_start=datetime.strptime('2020-02-25', '%Y-%m-%d'),
                target_end_date=datetime.strptime('2020-03-02', '%Y-%m-%d'))

ColorTracking = Project(name = 'Color Tracking', site_id=kgh.id, status_id=stat_inProg.id, typeOfWork_id=CT.id, 
                description = 'Build out UPaintDB for color tracking',
                date_start=datetime.strptime('2020-01-01', '%Y-%m-%d'))


db.session.add(vjhMedRec)
db.session.add(KGHPaintSchedule)
db.session.add(PolExtWinter2020)
db.session.add(AWARooms)
db.session.add(Gamma2)
db.session.add(CancerStaffRoom)
db.session.add(StrathChapel)
db.session.add(ColorTracking)

db.session.commit()

print("February Projects Added")

from ultradb.models import Timesheet

####### Russ' Hours
# Week 1
rts1 = Timesheet(dateOfWork=datetime.strptime('2020-02-03', "%Y-%m-%d"), dateSubmit=dt, user_id=russ.id, project_id=vjhMedRec.id, hours=10, comment='NA', isNotWorkDay=False, completed=True)
rts2 = Timesheet(dateOfWork=datetime.strptime('2020-02-04', "%Y-%m-%d"), dateSubmit=dt, user_id=russ.id, project_id=vjhMedRec.id, hours=10, comment='NA', isNotWorkDay=False, completed=True)
rts3 = Timesheet(dateOfWork=datetime.strptime('2020-02-05', "%Y-%m-%d"), dateSubmit=dt, user_id=russ.id, project_id=vjhMedRec.id, hours=10, comment='NA', isNotWorkDay=False, completed=True)
rts4 = Timesheet(dateOfWork=datetime.strptime('2020-02-06', "%Y-%m-%d"), dateSubmit=dt, user_id=russ.id, project_id=vjhMedRec.id, hours=10, comment='NA', isNotWorkDay=False, completed=True)

db.session.add(rts1)
db.session.add(rts2)
db.session.add(rts3)
db.session.add(rts4)

rts1.user.append(russ)
rts2.user.append(russ)
rts3.user.append(russ)
rts4.user.append(russ)

rts1.project.append(vjhMedRec)
rts2.project.append(vjhMedRec)
rts3.project.append(vjhMedRec)
rts4.project.append(vjhMedRec)

# Week 2
rts5 = Timesheet(dateOfWork=datetime.strptime('2020-02-10', "%Y-%m-%d"), dateSubmit=dt, user_id=russ.id, project_id=vjhMedRec.id, hours=10, comment='NA', isNotWorkDay=False, completed=True)
rts6 = Timesheet(dateOfWork=datetime.strptime('2020-02-11', "%Y-%m-%d"), dateSubmit=dt, user_id=russ.id, project_id=vjhMedRec.id, hours=10, comment='NA', isNotWorkDay=False, completed=True)
rts7 = Timesheet(dateOfWork=datetime.strptime('2020-02-12', "%Y-%m-%d"), dateSubmit=dt, user_id=russ.id, project_id=PolExtWinter2020.id, hours=10, comment='NA', isNotWorkDay=False, completed=True)
rts8 = Timesheet(dateOfWork=datetime.strptime('2020-02-13', "%Y-%m-%d"), dateSubmit=dt, user_id=russ.id, project_id=PolExtWinter2020.id, hours=10, comment='NA', isNotWorkDay=False, completed=True)

db.session.add(rts5)
db.session.add(rts6)
db.session.add(rts7)
db.session.add(rts8)

rts5.user.append(russ)
rts6.user.append(russ)
rts7.user.append(russ)
rts8.user.append(russ)

rts5.project.append(vjhMedRec)
rts6.project.append(vjhMedRec)
rts7.project.append(PolExtWinter2020)
rts8.project.append(PolExtWinter2020)

# Week 3
rts9 = Timesheet(dateOfWork=datetime.strptime('2020-02-17', "%Y-%m-%d"), dateSubmit=dt, user_id=russ.id, project_id=vjhMedRec.id, hours=8, comment='NA', isNotWorkDay=False, completed=True)
rts10 = Timesheet(dateOfWork=datetime.strptime('2020-02-18', "%Y-%m-%d"), dateSubmit=dt, user_id=russ.id, project_id=vjhMedRec.id, hours=8, comment='NA', isNotWorkDay=False, completed=True)
rts11 = Timesheet(dateOfWork=datetime.strptime('2020-02-19', "%Y-%m-%d"), dateSubmit=dt, user_id=russ.id, project_id=AWARooms.id, hours=10, comment='NA', isNotWorkDay=False, completed=True)
rts12 = Timesheet(dateOfWork=datetime.strptime('2020-02-20', "%Y-%m-%d"), dateSubmit=dt, user_id=russ.id, project_id=AWARooms.id, hours=10, comment='NA', isNotWorkDay=False, completed=True)

db.session.add(rts9)
db.session.add(rts10)
db.session.add(rts11)
db.session.add(rts12)

rts9.user.append(russ)
rts10.user.append(russ)
rts11.user.append(russ)
rts12.user.append(russ)

rts9.project.append(vjhMedRec)
rts10.project.append(vjhMedRec)
rts11.project.append(AWARooms)
rts12.project.append(AWARooms)

# Week 4
rts13 = Timesheet(dateOfWork=datetime.strptime('2020-02-25', "%Y-%m-%d"), dateSubmit=dt, user_id=russ.id, project_id=PolExtWinter2020.id, hours=6, comment='NA', isNotWorkDay=False, completed=True)
rts14 = Timesheet(dateOfWork=datetime.strptime('2020-02-25', "%Y-%m-%d"), dateSubmit=dt, user_id=russ.id, project_id=AWARooms.id, hours=4, comment='NA', isNotWorkDay=False, completed=True)
rts15 = Timesheet(dateOfWork=datetime.strptime('2020-02-26', "%Y-%m-%d"), dateSubmit=dt, user_id=russ.id, project_id=PolExtWinter2020.id, hours=10, comment='NA', isNotWorkDay=False, completed=True)
rts16 = Timesheet(dateOfWork=datetime.strptime('2020-02-27', "%Y-%m-%d"), dateSubmit=dt, user_id=russ.id, project_id=PolExtWinter2020.id, hours=6, comment='NA', isNotWorkDay=False, completed=True)
rts17 = Timesheet(dateOfWork=datetime.strptime('2020-02-27', "%Y-%m-%d"), dateSubmit=dt, user_id=russ.id, project_id=Gamma2.id, hours=2.5, comment='NA', isNotWorkDay=False, completed=True)
rts18 = Timesheet(dateOfWork=datetime.strptime('2020-02-27', "%Y-%m-%d"), dateSubmit=dt, user_id=russ.id, project_id=CancerStaffRoom.id, hours=2, comment='NA', isNotWorkDay=False, completed=True)

db.session.add(rts13)
db.session.add(rts14)
db.session.add(rts15)
db.session.add(rts16)
db.session.add(rts17)
db.session.add(rts18)

rts13.user.append(russ)
rts14.user.append(russ)
rts15.user.append(russ)
rts16.user.append(russ)
rts17.user.append(russ)
rts18.user.append(russ)

rts13.project.append(PolExtWinter2020)
rts14.project.append(AWARooms)
rts15.project.append(PolExtWinter2020)
rts16.project.append(PolExtWinter2020)
rts17.project.append(Gamma2)
rts18.project.append(CancerStaffRoom)

####### Chris' Hours
# Week 1
cts1 = Timesheet(dateOfWork=datetime.strptime('2020-02-03', "%Y-%m-%d"), dateSubmit=dt, user_id=chris.id, project_id=vjhMedRec.id, hours=10, comment='NA', isNotWorkDay=False, completed=True)
cts2 = Timesheet(dateOfWork=datetime.strptime('2020-02-04', "%Y-%m-%d"), dateSubmit=dt, user_id=chris.id, project_id=vjhMedRec.id, hours=10, comment='NA', isNotWorkDay=False, completed=True)
cts3 = Timesheet(dateOfWork=datetime.strptime('2020-02-05', "%Y-%m-%d"), dateSubmit=dt, user_id=chris.id, project_id=vjhMedRec.id, hours=10, comment='NA', isNotWorkDay=False, completed=True)
cts4 = Timesheet(dateOfWork=datetime.strptime('2020-02-06', "%Y-%m-%d"), dateSubmit=dt, user_id=chris.id, project_id=vjhMedRec.id, hours=10, comment='NA', isNotWorkDay=False, completed=True)

db.session.add(cts1)
db.session.add(cts2)
db.session.add(cts3)
db.session.add(cts4)

cts1.user.append(chris)
cts2.user.append(chris)
cts3.user.append(chris)
cts4.user.append(chris)

cts1.project.append(vjhMedRec)
cts2.project.append(vjhMedRec)
cts3.project.append(vjhMedRec)
cts4.project.append(vjhMedRec)

# Week 2
cts5 = Timesheet(dateOfWork=datetime.strptime('2020-02-10', "%Y-%m-%d"), dateSubmit=dt, user_id=chris.id, project_id=vjhMedRec.id, hours=10, comment='NA', isNotWorkDay=False, completed=True)
cts6 = Timesheet(dateOfWork=datetime.strptime('2020-02-11', "%Y-%m-%d"), dateSubmit=dt, user_id=chris.id, project_id=vjhMedRec.id, hours=10, comment='NA', isNotWorkDay=False, completed=True)
cts7 = Timesheet(dateOfWork=datetime.strptime('2020-02-12', "%Y-%m-%d"), dateSubmit=dt, user_id=chris.id, project_id=PolExtWinter2020.id, hours=10, comment='NA', isNotWorkDay=False, completed=True)
cts8 = Timesheet(dateOfWork=datetime.strptime('2020-02-13', "%Y-%m-%d"), dateSubmit=dt, user_id=chris.id, project_id=PolExtWinter2020.id, hours=10, comment='NA', isNotWorkDay=False, completed=True)

db.session.add(cts5)
db.session.add(cts6)
db.session.add(cts7)
db.session.add(cts8)

cts5.user.append(chris)
cts6.user.append(chris)
cts7.user.append(chris)
cts8.user.append(chris)

cts5.project.append(vjhMedRec)
cts6.project.append(vjhMedRec)
cts7.project.append(PolExtWinter2020)
cts8.project.append(PolExtWinter2020)

# Week 3
cts9 = Timesheet(dateOfWork=datetime.strptime('2020-02-17', "%Y-%m-%d"), dateSubmit=dt, user_id=chris.id, project_id=vjhMedRec.id, hours=8, comment='NA', isNotWorkDay=False, completed=True)
cts10 = Timesheet(dateOfWork=datetime.strptime('2020-02-18', "%Y-%m-%d"), dateSubmit=dt, user_id=chris.id, project_id=vjhMedRec.id, hours=10, comment='NA', isNotWorkDay=False, completed=True)
cts11 = Timesheet(dateOfWork=datetime.strptime('2020-02-19', "%Y-%m-%d"), dateSubmit=dt, user_id=chris.id, project_id=AWARooms.id, hours=10, comment='NA', isNotWorkDay=False, completed=True)
cts12 = Timesheet(dateOfWork=datetime.strptime('2020-02-20', "%Y-%m-%d"), dateSubmit=dt, user_id=chris.id, project_id=AWARooms.id, hours=10, comment='NA', isNotWorkDay=False, completed=True)

db.session.add(cts9)
db.session.add(cts10)
db.session.add(cts11)
db.session.add(cts12)

cts9.user.append(chris)
cts10.user.append(chris)
cts11.user.append(chris)
cts12.user.append(chris)

cts9.project.append(vjhMedRec)
cts10.project.append(vjhMedRec)
cts11.project.append(AWARooms)
cts12.project.append(AWARooms)

# Week 4
cts13 = Timesheet(dateOfWork=datetime.strptime('2020-02-24', "%Y-%m-%d"), dateSubmit=dt, user_id=chris.id, project_id=PolExtWinter2020.id, hours=10.5, comment='NA', isNotWorkDay=False, completed=True)
cts14 = Timesheet(dateOfWork=datetime.strptime('2020-02-25', "%Y-%m-%d"), dateSubmit=dt, user_id=chris.id, project_id=PolExtWinter2020.id, hours=6, comment='NA', isNotWorkDay=False, completed=True)
# Missing 4 hours for Chris, guessing it was in AWA with russ though...
# cts14 = Timesheet(dateOfWork=datetime.strptime('2020-02-25', "%Y-%m-%d"), dateSubmit=dt, user_id=chris.id, project_id=AWARooms.id, hours=4, comment='NA', isNotWorkDay=False, completed=True)

cts15 = Timesheet(dateOfWork=datetime.strptime('2020-02-26', "%Y-%m-%d"), dateSubmit=dt, user_id=chris.id, project_id=PolExtWinter2020.id, hours=10, comment='NA', isNotWorkDay=False, completed=True)
cts16 = Timesheet(dateOfWork=datetime.strptime('2020-02-27', "%Y-%m-%d"), dateSubmit=dt, user_id=chris.id, project_id=PolExtWinter2020.id, hours=2, comment='NA', isNotWorkDay=False, completed=True)
cts17 = Timesheet(dateOfWork=datetime.strptime('2020-02-27', "%Y-%m-%d"), dateSubmit=dt, user_id=chris.id, project_id=Gamma2.id, hours=3, comment='NA', isNotWorkDay=False, completed=True)
cts18 = Timesheet(dateOfWork=datetime.strptime('2020-02-27', "%Y-%m-%d"), dateSubmit=dt, user_id=chris.id, project_id=CancerStaffRoom.id, hours=2, comment='NA', isNotWorkDay=False, completed=True)
# Missing 3 hours for Chris here as well... Find project and Uncomment
# cts19 = Timesheet(dateOfWork=datetime.strptime('2020-02-27', "%Y-%m-%d"), dateSubmit=dt, user_id=chris.id, project_id=.id, hours=3, comment='NA', isNotWorkDay=False, completed=True)

db.session.add(cts12)
db.session.add(cts13)
db.session.add(cts15)
db.session.add(cts16)
db.session.add(cts17)
db.session.add(cts18)

cts13.user.append(chris)
cts14.user.append(chris)
cts15.user.append(chris)
cts16.user.append(chris)
cts17.user.append(chris)
cts18.user.append(chris)

cts13.project.append(PolExtWinter2020)
cts14.project.append(PolExtWinter2020)
cts15.project.append(PolExtWinter2020)
cts16.project.append(PolExtWinter2020)
cts17.project.append(Gamma2)
cts18.project.append(CancerStaffRoom)

###### Steve's Hours
# Week 1
sts1 = Timesheet(dateOfWork=datetime.strptime('2020-02-05', "%Y-%m-%d"), dateSubmit=dt, user_id=steve.id, project_id=vjhMedRec.id, hours=2.5, comment='NA', isNotWorkDay=False, completed=True)
sts2 = Timesheet(dateOfWork=datetime.strptime('2020-02-06', "%Y-%m-%d"), dateSubmit=dt, user_id=steve.id, project_id=vjhMedRec.id, hours=4, comment='NA', isNotWorkDay=False, completed=True)
sts3 = Timesheet(dateOfWork=datetime.strptime('2020-02-07', "%Y-%m-%d"), dateSubmit=dt, user_id=steve.id, project_id=KGHPaintSchedule.id, hours=4, comment='NA', isNotWorkDay=False, completed=True)

db.session.add(sts1)
db.session.add(sts2)
db.session.add(sts3)

sts1.user.append(steve)
sts2.user.append(steve)
sts3.user.append(steve)

sts1.project.append(vjhMedRec)
sts2.project.append(vjhMedRec)
sts3.project.append(KGHPaintSchedule)

# Week 2
sts4 = Timesheet(dateOfWork=datetime.strptime('2020-02-10', "%Y-%m-%d"), dateSubmit=dt, user_id=steve.id, project_id=PolExtWinter2020.id, hours=5.5, comment='NA', isNotWorkDay=False, completed=True)
sts5 = Timesheet(dateOfWork=datetime.strptime('2020-02-11', "%Y-%m-%d"), dateSubmit=dt, user_id=steve.id, project_id=vjhMedRec.id, hours=5.5, comment='NA', isNotWorkDay=False, completed=True)
sts6 = Timesheet(dateOfWork=datetime.strptime('2020-02-13', "%Y-%m-%d"), dateSubmit=dt, user_id=steve.id, project_id=PolExtWinter2020.id, hours=4, comment='NA', isNotWorkDay=False, completed=True)

db.session.add(sts4)
db.session.add(sts5)
db.session.add(sts6)

sts4.user.append(steve)
sts5.user.append(steve)
sts6.user.append(steve)

sts4.project.append(PolExtWinter2020)
sts5.project.append(vjhMedRec)
sts6.project.append(PolExtWinter2020)

# Week 3
sts7 = Timesheet(dateOfWork=datetime.strptime('2020-02-18', "%Y-%m-%d"), dateSubmit=dt, user_id=steve.id, project_id=PolExtWinter2020.id, hours=2, comment='NA', isNotWorkDay=False, completed=True)

db.session.add(sts7)

sts7.user.append(steve)

sts7.project.append(PolExtWinter2020)

# Week 4
sts8 = Timesheet(dateOfWork=datetime.strptime('2020-02-24', "%Y-%m-%d"), dateSubmit=dt, user_id=steve.id, project_id=PolExtWinter2020.id, hours=5.5, comment='NA', isNotWorkDay=False, completed=True)
sts9 = Timesheet(dateOfWork=datetime.strptime('2020-02-26', "%Y-%m-%d"), dateSubmit=dt, user_id=steve.id, project_id=StrathChapel.id, hours=8.5, comment='NA', isNotWorkDay=False, completed=True)

db.session.add(sts8)
db.session.add(sts9)

sts8.user.append(steve)
sts9.user.append(steve)

sts8.project.append(PolExtWinter2020)
sts9.project.append(StrathChapel)

###### Dans Hours
# Week 2
dts1 = Timesheet(dateOfWork=datetime.strptime('2020-02-12', "%Y-%m-%d"), dateSubmit=dt, user_id=dan.id, project_id=ColorTracking.id, hours=4, comment='NA', isNotWorkDay=False, completed=True)
dts2 = Timesheet(dateOfWork=datetime.strptime('2020-02-13', "%Y-%m-%d"), dateSubmit=dt, user_id=dan.id, project_id=ColorTracking.id, hours=4, comment='NA', isNotWorkDay=False, completed=True)

db.session.add(dts1)
db.session.add(dts2)

dts1.user.append(dan)
dts2.user.append(dan)

dts1.project.append(ColorTracking)
dts2.project.append(ColorTracking)

# Week 3
dts3 = Timesheet(dateOfWork=datetime.strptime('2020-02-16', "%Y-%m-%d"), dateSubmit=dt, user_id=dan.id, project_id=ColorTracking.id, hours=4, comment='NA', isNotWorkDay=False, completed=True)
dts4 = Timesheet(dateOfWork=datetime.strptime('2020-02-17', "%Y-%m-%d"), dateSubmit=dt, user_id=dan.id, project_id=ColorTracking.id, hours=2, comment='NA', isNotWorkDay=False, completed=True)
dts5 = Timesheet(dateOfWork=datetime.strptime('2020-02-18', "%Y-%m-%d"), dateSubmit=dt, user_id=dan.id, project_id=ColorTracking.id, hours=3, comment='NA', isNotWorkDay=False, completed=True)

db.session.add(dts3)
db.session.add(dts4)
db.session.add(dts5)

dts3.user.append(dan)
dts4.user.append(dan)
dts5.user.append(dan)

dts3.project.append(ColorTracking)
dts4.project.append(ColorTracking)
dts5.project.append(ColorTracking)

# Week 4
dts6 = Timesheet(dateOfWork=datetime.strptime('2020-02-23', "%Y-%m-%d"), dateSubmit=dt, user_id=dan.id, project_id=ColorTracking.id, hours=6, comment='NA', isNotWorkDay=False, completed=True)
dts7 = Timesheet(dateOfWork=datetime.strptime('2020-02-23', "%Y-%m-%d"), dateSubmit=dt, user_id=dan.id, project_id=StrathChapel.id, hours=8.5, comment='Sanded walls, double primed wood, and painted walls and Ceilings', isNotWorkDay=False, completed=True)
dts8 = Timesheet(dateOfWork=datetime.strptime('2020-02-27', "%Y-%m-%d"), dateSubmit=dt, user_id=dan.id, project_id=ColorTracking.id, hours=4, comment='NA', isNotWorkDay=False, completed=True)

db.session.add(dts6)
db.session.add(dts7)
db.session.add(dts8)

dts6.user.append(dan)
dts7.user.append(dan)
dts8.user.append(dan)

dts6.project.append(ColorTracking)
dts7.project.append(StrathChapel)
dts8.project.append(ColorTracking)

db.session.commit()

print("February Timesheets added")







