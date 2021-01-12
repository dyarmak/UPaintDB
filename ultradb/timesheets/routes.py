from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from ultradb.timesheets.forms import TimesheetForm, TimesheetDateRangeForm
from ultradb.models import User, Project, Timesheet
from ultradb import db
from flask_login import current_user, login_required
from sqlalchemy import desc, and_
from datetime import datetime, timedelta

from ultradb.auth.utils import roleAuth
from ultradb.timesheets.ts_utils import send_payroll_email

timesheet_bp = Blueprint('timesheet_bp', __name__)

from ultradb.timesheets.ts_utils import get_timesheets, timesheet_to_email

# Employee Hours Review
@timesheet_bp.route("/timesheet/review", methods=['GET', 'POST'])
@login_required
def employee_hours_review():
    # Get Timesheets as a DataFrame
    tsdf = get_timesheets(current_user)
    # Build the Most recent 2 weeks hours into an email message
    sub, msg, m = timesheet_to_email(tsdf) 
    sub2, msg2, m2 = timesheet_to_email(tsdf, 1)

    return render_template('timesheet_employee_review.html', title='Review Timesheet', legend='Review Timesheet', msg=msg, msg2=msg2)

@timesheet_bp.route("/timesheet/review/sendemail/<int:weekno>", methods=['GET', 'POST'])
@login_required
def employee_hours_submit(weekno):
    user = current_user
    # Get Timesheets as a DataFrame
    tsdf = get_timesheets(current_user)
    
    # use the weekno to determine which to send
    if weekno == 0:
        sub, msg, m = timesheet_to_email(tsdf) 
        print("sub: " + str(sub))
        print("m: " + str(m))
        send_payroll_email(user, sub, m)
        flash('Hours sent to Steve via email. A copy has been sent to your inbox.', 'success')
    if weekno == 1:    
        sub, msg, m = timesheet_to_email(tsdf, 1)
        send_payroll_email(user, sub, m)
        flash('Hours sent to Steve via email. A copy has been sent to your inbox.', 'success')
    
    return redirect(url_for('timesheet_bp.view_timesheet'))


# Delete a Timesheet Entry
@timesheet_bp.route("/timesheet/<int:ts_id>/delete", methods=['POST'])
@login_required
def delete_ts_entry(ts_id):
    ts = Timesheet.query.get_or_404(ts_id)
    # check that the TS belongs to the current user.
    if ts.user_id != current_user.id:
        abort(403)
    db.session.delete(ts)
    db.session.commit()
    flash('Your timesheet entry has been deleted!', 'success')
    return redirect(url_for('timesheet_bp.add_timesheet'))

# Complete a Timesheet for given day route
@timesheet_bp.route("/completeTS/<date>")
@login_required
def complete_day(date):
    curUser_id = current_user.id
    user = User.query.get(curUser_id)
    # get all ts for user
    tss = Timesheet.query.filter_by(user_id=user.id).filter_by(date_of_work=date)
    for ts in tss:
        ts.completed = True
        db.session.commit()
    return redirect(url_for('timesheet_bp.view_timesheet'))


# Display Timesheet Entries
@timesheet_bp.route("/timesheet", methods=['GET', 'POST'])
@login_required
def view_timesheet():
    form=TimesheetDateRangeForm()
    curUser_id = current_user.id
    user = User.query.get(curUser_id)
    tss = Timesheet.query.filter_by(user_id=user.id).order_by(desc(Timesheet.date_of_work))

    if form.validate_on_submit():
        # apply the date range filter
        tss = Timesheet.query.filter_by(user_id=user.id).filter(and_(Timesheet.date_of_work >= form.startDate.data, Timesheet.date_of_work <= form.endDate.data)).order_by(desc(Timesheet.date_of_work))


    return render_template('timesheet.html', title='View Timesheets', legend='View Timesheet', tss=tss, user=user, form=form)


# Timesheet Entry
@timesheet_bp.route("/timesheet/add", methods=['GET', 'POST'])
@login_required
def add_timesheet():
    form=TimesheetForm()
    # Projects ordered most recent start_date first
    project_query = Project.query.filter(Project.status_id.in_([1,2,3,4])).order_by(desc(Project.date_start))
    form.project_id.query = project_query
    user = User.query.get(current_user.id)
    # Need to initialize this to prevent crashes
    prevts = None
    dateLastEntry = None

    if request.method == 'GET':
        # Check for an umcompleted day
        uncompleteDay = Timesheet.query.filter_by(user_id = user.id).filter_by(completed=False).first()
        
        # IF there is an uncompleted day we set the date_of_work field in the form to be that date
        if uncompleteDay:
            dateLastEntry = uncompleteDay.date_of_work
            form.date_of_work.data = dateLastEntry
            # Query and display the other entries on this uncomplete day
            prevts = Timesheet.query.filter_by(user_id = user.id).filter_by(date_of_work=dateLastEntry)
            

        # If no uncompleteDay, we check for the last entry.
        else:
            lastEntry = Timesheet.query.filter_by(user_id = user.id).filter_by(completed=True).order_by(desc(Timesheet.date_of_work)).first() 
            
            #  If there is a lastEntry, we can set the form value to the day after the most recent entry
            if lastEntry:
                dateLastEntry = lastEntry.date_of_work
                formDateValue = dateLastEntry + timedelta(days=1)
            
            # in the event of a new hire, lastEntry will return None, so we will need to set the form value to today
            else:
                formDateValue = datetime.now().date()
            
            # now it is safe to set the form value. 
            form.date_of_work.data = formDateValue
            

    if form.validate_on_submit():
        completed = form.completed.data 
        # completed = False # WAS the default value for a new entry.
        curUser = User.query.get(current_user.id)
        proj = Project.query.get(form.project_id.data.id)
            
        newTimesheet = Timesheet(date_submit=datetime.utcnow(), 
                                date_of_work=form.date_of_work.data, project_id=form.project_id.data.id, 
                                hours=form.hours.data, comment=form.comment.data,
                                user_id=curUser.id, completed=completed)
        db.session.add(newTimesheet)

        # Add to project_timesheet table
        proj.timesheets.append(newTimesheet)
        # Add to UserTimesheet table
        newTimesheet.user.append(curUser)
        db.session.commit()
        flash('Time Entered Successfully!', 'success')

        if (completed == False):
            return redirect(url_for('timesheet_bp.add_timesheet'))
        else:
            return redirect(url_for('timesheet_bp.view_timesheet'))

    return render_template('timesheet_add.html', title='Enter Your Time', legend='Enter Your Time', tss=prevts, dateLastEntry=dateLastEntry, form=form, user=user)


