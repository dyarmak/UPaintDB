from ultradb import db, create_app


# Create app and app context
app = create_app()
app.app_context().push()

from datetime import datetime
from ultradb.models import Timesheet

# Function for adding TS Entries
def addTS(emp, dateStr, proj, hrs, cmt):
        dt = datetime.utcnow()
        ts = Timesheet(dateOfWork=datetime.strptime(dateStr, "%Y-%m-%d"), 
        dateSubmit=dt, user_id=emp.id, 
        project_id=proj.id, hours=hrs, 
        comment=cmt, 
        isNotWorkDay=False, completed=True)
        
        db.session.add(ts)
        ts.user.append(emp)
        ts.project.append(proj)
        db.session.commit()