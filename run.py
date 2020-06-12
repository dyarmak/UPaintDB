from ultradb import db, create_app
from ultradb.models import (User, Post, Site, Area, Room, ColorSheet, Worktype, Status, 
                            Timesheet, Project, Supplier, Brand, Product, Sheen, Paint,
                            Color, PaintColor, user_timesheet, project_area, project_room,
                            Client)

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

# This allows me to type into the command line:
# (venv) PS C:\..\UltraSiteDB> flask shell
# and it will do the imports of the items listed in the dict below
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Site': Site, 'Area': Area, 'Room': Room, 
    'ColorSheet': ColorSheet, 'Worktype':Worktype, 'Status':Status, 'Timesheet':Timesheet, 'Project':Project,
    'Supplier':Supplier, 'Brand':Brand, 'Product':Product, 'Sheen':Sheen, 'Paint':Paint, 'Color':Color, 
    'PaintColor':PaintColor, 'user_timesheet':user_timesheet, 'project_area':project_area, 'project_room':project_room,
    'Client':Client}