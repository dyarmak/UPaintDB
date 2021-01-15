from flask import Blueprint, flash
from flask_login import login_required
from ultradb.timesheets.forms import TimesheetForm
from ultradb.models import Timesheet, User, Project
from flask import render_template, url_for, redirect, request
from ultradb import db
from ultradb.auth.utils import roleAuth
from sqlalchemy import and_
from datetime import datetime, timedelta

admin_bp = Blueprint('admin_bp', __name__)

from ultradb.timesheets.ts_utils import get_timesheets, timesheet_to_email, timesheet_to_email_summarized

# Payroll Review
@admin_bp.route("/admin/payroll")
@login_required
def admin_payroll_review():
    # Must be Admin
    if not roleAuth('Admin'):
        return redirect(url_for('main_bp.home'))
    
    # Build the Most recent weeks Payroll Emails
    tsdf = get_timesheets()
    sub1, msg1, m1 = timesheet_to_email_summarized(tsdf)
    sub2, msg2, m2 = timesheet_to_email(tsdf)


    return render_template("admin_payroll_review.html", title="Admin", sub1=sub1, msg1=msg1, sub2=sub2, msg2=msg2)

# Admin create a new timesheet entry.
@admin_bp.route("/admin/review/add", methods=['GET','POST'])
@login_required
def admin_create_ts_entry():
    # Must be Admin
    if not roleAuth('Admin'):
        return redirect(url_for('main_bp.home'))
    
    form=TimesheetForm()
    
    if form.validate_on_submit():
        employee = User.query.get(form.user_id.data.id)
        proj = Project.query.get(form.project_id.data.id)
        
        ts = Timesheet(date_submit=datetime.utcnow(), 
                       user_id= employee.id,
                       date_of_work = form.date_of_work.data, 
                       project_id = form.project_id.data.id,
                       hours = form.hours.data,
                       comment = form.comment.data)
        db.session.add(ts)

        # Add to project_timesheet table
        proj.timesheets.append(ts)
        # Add to UserTimesheet table
        ts.user.append(employee)
        db.session.commit()

        msg = f'Timesheet entry created successfully'
        flash(msg, 'success')
        return redirect(url_for('admin_bp.admin_review'))

    return render_template("admin_create_TS.html", form=form)

# Admin a Timesheet Delete
@admin_bp.route("/admin/review/delete/<int:ts_id>", methods=['POST'])
@login_required
def delete_ts_entry(ts_id):
    # Must be Admin
    if not roleAuth('Admin'):
        return redirect(url_for('main_bp.home'))
    
    ts = Timesheet.query.get_or_404(ts_id)

    db.session.delete(ts)
    db.session.commit()
    flash('The timesheet entry has been deleted!', 'success')
    return redirect(url_for('admin_bp.admin_review'))

# Admin Timesheet Edit
@admin_bp.route("/admin/review/update/<int:ts_id>", methods=['GET', 'POST'])
@login_required
def admin_timesheet_update(ts_id):
    # Must be Admin
    if not roleAuth('Admin'):
        return redirect(url_for('main_bp.home'))
    
    ts = Timesheet.query.get(ts_id)
    form = TimesheetForm()
    user = ts.user.first()

    if form.validate_on_submit():
        ts.date_of_work = form.date_of_work.data
        ts.project_id = form.project_id.data.id
        ts.hours = form.hours.data
        ts.comment = form.comment.data

        db.session.commit()

        msg = f'Timesheet for {ts.user.first().username} updated successfully'
        flash(msg, 'success')
        return redirect(url_for('admin_bp.admin_review'))

    elif request.method== 'GET':
        form.date_of_work.data = ts.date_of_work
        form.project_id.data = Project.query.get(ts.project_id)
        form.hours.data = ts.hours
        form.comment.data = ts.comment

    return render_template("timesheet_update.html", ts_id=ts.id, form=form, user=user)


# Admin Control Panel
@admin_bp.route("/admin")
@login_required
def admincp():
    # Must be Admin
    if not roleAuth('Admin'):
        return redirect(url_for('main_bp.home'))

    # get list of Employees, show they're average daily, weekly, monthly hours (some stats)
    users = User.query.all()

    # Add new Employee

    # We need to be able to change Users' attributes from the control panel. 
    # Update Access Level and isEmployed 


    # Review / Approve / Edit Employee Time Entries
        # done on a different Route


    return render_template("admin_cp.html", title="Admin", users=users)


# Admin Hours Review
@admin_bp.route("/admin/review")
@login_required
def admin_review():
    # Must be Admin
    if not roleAuth('Admin'):
        return redirect(url_for('main_bp.home'))
    # Review / Approve / Edit Employee Time Entries
    
    # We want to get those timesheets within the last month / 30 days.
    numDays = 30 # using 90 because we don't have anything more recent. 
    startDate = datetime.now().date()
    endDate = startDate-timedelta(days=numDays)

    # Get the last 30 days worth of Timesheets
    tss = Timesheet.query.filter(and_(Timesheet.date_of_work <= startDate, Timesheet.date_of_work >= endDate)).order_by(Timesheet.approved.asc()).order_by(Timesheet.date_of_work.desc()).order_by(Timesheet.user_id)

    return render_template("admin_review.html", title="Timesheet Review", tss=tss)


@admin_bp.route("/admin/review/approve/<int:ts_id>")
@login_required
def admin_approve(ts_id):
    # Must be Admin
    if not roleAuth('Admin'):
        return redirect(url_for('main_bp.home'))
    
    ts = Timesheet.query.get(ts_id)
    ts.approved = True
    db.session.commit()
    return redirect(url_for('admin_bp.admin_review'))

@admin_bp.route("/admin/review/unapprove/<int:ts_id>")
@login_required
def admin_unapprove(ts_id):
    # Must be Admin
    if not roleAuth('Admin'):
        return redirect(url_for('main_bp.home'))
    
    ts = Timesheet.query.get(ts_id)
    ts.approved = False
    db.session.commit()
    return redirect(url_for('admin_bp.admin_review'))

