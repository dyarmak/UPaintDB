from ultradb import app, db
from ultradb.models import (User, Post, Site, Area, Room, ColorSheet, Type, Status, 
                            Timesheet, Project, Supplier, Brand, Product, Sheen, Paint,
                            Color, PaintColor, user_timesheet, project_area, project_room)

# Functions for interacting with queries
# Get a project to work from
p = Project.query.get(3)
# p is project with id=3, in this case the VJH MRI project

# Projects have a timesheets attribute that we can access like this
p.timesheets
# This returns an sa.orm.dynamic.AppenderBaseQuery object

# we call meth:all() on it to display all the objects
p.timesheets.all()
# This will return a list of all the timesheet objects for the project

# We can access elements in the list with [] notation
p.timesheets.all()[0]
# returns the timesheet object, 
# which we can then further query its attributes, like its user
p.timesheets.all()[1].user
# which again returns an AppenderBaseQuery
p.timesheets.all()[1].user.first() 
# Finally, we can access the attributes of the selected User
p.timesheets.all()[1].user.first().lName


# Same goes for class:Timesheet
ts = Timesheet.query.get(5)
ts.user.first().fName

# and for class:User
u = User.query.get(1)
u.timesheets.all()[4].hours
