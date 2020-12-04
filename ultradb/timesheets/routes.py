from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from ultradb.timesheets.forms import TimesheetForm, TimesheetDateRangeForm
from ultradb.models import User, Project, Timesheet
from ultradb import db
from flask_login import current_user, login_required
from sqlalchemy import desc, and_
from datetime import datetime, timedelta

from ultradb.auth.utils import roleAuth

timesheet_bp = Blueprint('timesheet_bp', __name__)

# Display Timesheet Entries
@timesheet_bp.route("/timesheet/adminReview", methods=['GET', 'POST'])
@login_required
def timesheet_review():
    # Must be Admin
    if not roleAuth('Admin'):
        return redirect(url_for('main_bp.home'))

    users = User.query.all()

    # Get 30 day date range
    startDate = datetime.now().date()
    endDate = startDate-timedelta(days=90)

    # Get the last 30 days worth of Timesheets
    tss = Timesheet.query.filter(and_(Timesheet.dateOfWork <= startDate, Timesheet.dateOfWork >= endDate)).order_by(desc(Timesheet.dateOfWork))


    return render_template('timesheet_review.html', title='View Timesheets', legend='View Timesheet', tss=tss)

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
    tss = Timesheet.query.filter_by(user_id=user.id).filter_by(dateOfWork=date)
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
    tss = Timesheet.query.filter_by(user_id=user.id).order_by(desc(Timesheet.dateOfWork))

    if form.validate_on_submit():
        # apply the date range filter
        tss = Timesheet.query.filter_by(user_id=user.id).filter(and_(Timesheet.dateOfWork >= form.startDate.data, Timesheet.dateOfWork <= form.endDate.data)).order_by(desc(Timesheet.dateOfWork))


    return render_template('timesheet.html', title='View Timesheets', legend='View Timesheet', tss=tss, user=user, form=form)


# Timesheet Entry
@timesheet_bp.route("/timesheet/add", methods=['GET', 'POST'])
@login_required
def add_timesheet():
    form=TimesheetForm()
    project_query = Project.query.filter(Project.status_id.in_([1,2,3,4]))
    form.project_id.query = project_query
    user = User.query.get(current_user.id)
    # Need to initialize this to prevent crashes
    prevts = None
    dateLastEntry = None

    if request.method == 'GET':
        # Check for an umcompleted day
        uncompleteDay = Timesheet.query.filter_by(user_id = user.id).filter_by(completed=False).first()
        
        # IF there is an uncompleted day we set the dateOfWork field in the form to be that date
        if uncompleteDay:
            dateLastEntry = uncompleteDay.dateOfWork
            form.dateOfWork.data = dateLastEntry
            # Query and display the other entries on this uncomplete day
            prevts = Timesheet.query.filter_by(user_id = user.id).filter_by(dateOfWork=dateLastEntry)
            

        # If no uncompleteDay, we check for the last entry.
        else:
            lastEntry = Timesheet.query.filter_by(user_id = user.id).filter_by(completed=True).order_by(desc(Timesheet.dateOfWork)).first() 
            
            #  If there is a lastEntry, we can set the form value to the day after the most recent entry
            if lastEntry:
                dateLastEntry = lastEntry.dateOfWork
                formDateValue = dateLastEntry + timedelta(days=1)
            
            # in the event of a new hire, lastEntry will return None, so we will need to set the form value to today
            else:
                formDateValue = datetime.now().date()
            
            # now it is safe to set the form value. 
            form.dateOfWork.data = formDateValue
            

    if form.validate_on_submit():
        completed = form.completed.data 
        # completed = False # WAS the default value for a new entry.
        curUser = User.query.get(current_user.id)
        proj = Project.query.get(form.project_id.data.id)
            
        newTimesheet = Timesheet(dateSubmit=datetime.utcnow(), 
                                dateOfWork=form.dateOfWork.data, project_id=form.project_id.data.id, 
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

    return render_template('add_timesheet.html', title='Enter Your Time', legend='Enter Your Time', tss=prevts, dateLastEntry=dateLastEntry, form=form, user=user)


