import os
import os.path
import boto3
import json
import secrets
import sqlite3
import pandas as pd
from jinjasql import JinjaSql
from datetime import datetime, timedelta, date
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from ultradb import app, db, bcrypt, mail
from ultradb.forms import (RegistrationForm, LoginForm, UpdateAccountForm, PostForm,
                           UpdateAreaForm, NewSiteForm, NewAreaForm, NewRoomForm, NewProjectForm, 
                           UpdateProjectForm, RequestResetForm, ResetPasswordForm, AddRoomToProjectForm,
                           AreaFilterForm, PaintColorBuilderForm, NewSupplierForm, NewBrandForm,
                           NewProductForm, NewColorForm, TimesheetForm, TimesheetDateRangeForm)
from ultradb.models import (User, Post, Site, Area, Room, ColorSheet, Project, Status, Worktype,
                            Supplier, Brand, Product, Sheen, Paint, Color, PaintColor, Timesheet)
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from sqlalchemy import desc, and_
from s3funcs import upload_file, download_file
from supfuncs import build_upcomingDF, build_asneededDF

# define the S3 bucket name
bucket='upaintdb-colorsheets'


# Display list of rooms in a site where date_next_paint <=1 year from today
@app.route("/site/<int:cur_site_id>/upcoming")
def upcoming(cur_site_id):
    site = Site.query.get_or_404(cur_site_id)
    site_id = site.id

    upcoming_rooms = build_upcomingDF(site_id)
    
    return render_template('site_upcoming.html', tables=[upcoming_rooms.to_html(classes='data')], titles=upcoming_rooms.columns.values, title='Upcoming Rooms', legend='Upcoming Rooms', site=site)


# Display list of rooms in a site where freq = -1 or "as needed"
@app.route("/site/<int:cur_site_id>/as_needed")
def as_needed(cur_site_id):
    site = Site.query.get_or_404(cur_site_id)
    site_id = site.id
    
    as_needed_rooms = build_asneededDF(site_id)

    return render_template('site_as_needed.html', tables=[as_needed_rooms.to_html(classes='data')], titles=as_needed_rooms.columns.values, title='As Needed Rooms', legend='As Needed Rooms', site=site)


#########################################################
################ BEGIN Timesheet Routes #################
#########################################################

# Delete a Timesheet Entry
@app.route("/timesheet/<int:ts_id>/delete", methods=['POST'])
@login_required
def delete_ts_entry(ts_id):
    ts = Timesheet.query.get_or_404(ts_id)
    if ts.user_id != current_user.id:
        abort(403)
    db.session.delete(ts)
    db.session.commit()
    flash('Your timesheet entry has been deleted!', 'success')
    return redirect(url_for('add_timesheet'))

# Complete a Timesheet for given day route
@app.route("/completeTS/<date>")
@login_required
def complete_day(date):
    curUser_id = current_user.id
    user = User.query.get(curUser_id)
    # get all ts for user
    tss = Timesheet.query.filter_by(user_id=user.id).filter_by(dateOfWork=date)
    for ts in tss:
        ts.completed = True
        db.session.commit()
    return redirect(url_for('view_timesheet'))


# Display Timesheet Entries
@app.route("/timesheet", methods=['GET', 'POST'])
@login_required
def view_timesheet():
    form=TimesheetDateRangeForm()
    curUser_id = current_user.id
    user = User.query.get(curUser_id)
    tss = Timesheet.query.filter_by(user_id=user.id).order_by(desc(Timesheet.dateOfWork))

    if form.validate_on_submit():
        tss = Timesheet.query.filter(and_(Timesheet.dateOfWork >= form.startDate.data, Timesheet.dateOfWork <= form.endDate.data)).order_by(desc(Timesheet.dateOfWork))


    return render_template('timesheet.html', title='View Timesheets', legend='View Timesheet', tss=tss, user=user, form=form)


# Timesheet Entry
@app.route("/timesheet/add", methods=['GET', 'POST'])
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
            

        # If not then set it equal to the day after the most recent entry
        else:
            lastEntry = Timesheet.query.filter_by(user_id = user.id).filter_by(completed=True).order_by(desc(Timesheet.dateOfWork)).first() 
            dateLastEntry = lastEntry.dateOfWork
            dateCurrentEntry = dateLastEntry + timedelta(days=1)
            form.dateOfWork.data = dateCurrentEntry
            # If dateCurrentEntry is a weekend, set workDay=False    
            if (dateCurrentEntry.weekday() >= 5):
                form.isNotWorkDay.data = True

    if form.validate_on_submit():
        completed = form.completed.data 
        # completed = False # WAS the default value for a new entry.
        curUser = User.query.get(current_user.id)
        proj = Project.query.get(form.project_id.data.id)
        # If box is checked, set day to completed
        if(form.isNotWorkDay.data == True):
            completed = True
            
        newTimesheet = Timesheet(dateSubmit=datetime.utcnow(), 
                                dateOfWork=form.dateOfWork.data, project_id=form.project_id.data.id, 
                                hours=form.hours.data, comment=form.comment.data,
                                user_id=curUser.id, isNotWorkDay=form.isNotWorkDay.data, completed=completed)
        db.session.add(newTimesheet)

        # Add to project_timesheet table
        proj.timesheets.append(newTimesheet)
        # Add to UserTimesheet table
        newTimesheet.user.append(curUser)
        db.session.commit()
        flash('Time Entered Successfully!', 'success')

        if (completed == False):
            return redirect(url_for('add_timesheet'))
        else:
            return redirect(url_for('view_timesheet'))

    return render_template('add_timesheet.html', title='Enter Your Time', legend='Enter Your Time', tss=prevts, dateLastEntry=dateLastEntry, form=form, user=user)


#########################################################
################ BEGIN Timesheet Routes #################
#########################################################





# View all projects (active projects filter?)
@app.route("/projects")
def project_list():
    projects = Project.query.all()
    return render_template('project_list.html', title='Project List', projects=projects)


# Add a new Project
@app.route("/newproject", methods=['GET', 'POST'])
def new_project():
    form = NewProjectForm()
    if form.validate_on_submit():
        project = Project(name= form.name.data,
                          site_id=form.site_id.data.id, 
                          status_id=form.status_id.data.id, 
                          typeOfWork_id=form.typeOfWork_id.data.id, 
                          description=form.description.data, 
                          date_start=form.date_start.data, 
                          target_end_date=form.target_end_date.data, 
                          hours_estimate= form.hours_estimate.data,
                          area_list= form.area_list.data,
                          quote_amt=form.quote_amt.data, 
                          damage_comment=form.damage_comment.data, 
                          extenuating_circumstances=form.extenuating_circumstances.data)
        db.session.add(project)
        db.session.commit()
        flash('New Project Added Successfully!', 'success')
        return redirect(url_for('home'))   
    return render_template('new_project.html', title='Add New Project', form=form, legend='Add a New Project')


# View Project details
@app.route("/projects/<int:cur_proj_id>")
def view_project(cur_proj_id):
    # get basic project info to display
    proj = Project.query.get_or_404(cur_proj_id)
    site = Site.query.get(proj.site_id)
    status = Status.query.get(proj.status_id)
    typeOfWork = Worktype.query.get(proj.typeOfWork_id)
    # Get list of areas in Project
    areas = proj.area_list
    # Get list of rooms in Project
    rooms = proj.room_list
    # get list of Timesheets for Project
    tss = proj.timesheets.all()
    # Sum up the total hours for display
    total_hours = 0
    for ts in tss:
        total_hours += ts.hours

    return render_template('view_project.html', title='Project Info', legend='Project Info', 
                        proj=proj, site=site, status=status, typeOfWork=typeOfWork, areas=areas, 
                        rooms=rooms, tss=tss, total_hours=total_hours)


# Update an existing Project, Add rooms and areas?
@app.route("/projects/<int:cur_proj_id>/update", methods=['GET', 'POST'])
def update_project(cur_proj_id):
    proj = Project.query.get_or_404(cur_proj_id)
    proj_site_id = proj.site_id
    site = Site.query.get(proj_site_id)
    form = UpdateProjectForm()  
    # This allows me to change the query and apply a filter to it for the page!
    form.area_list.query = Area.query.filter_by(site_id=proj.site_id)
    if form.validate_on_submit():
        proj.name = form.name.data 
        proj.site_id = form.site_id.data.id
        proj.status_id = form.status_id.data.id
        proj.typeOfWork_id = form.typeOfWork_id.data.id
        proj.description = form.description.data
        proj.date_start = form.date_start.data
        proj.target_end_date = form.target_end_date.data
        proj.hours_estimate = form.hours_estimate.data
        proj.quote_amt = form.quote_amt.data
        proj.damage_comment = form.damage_comment.data
        proj.extenuating_circumstances = form.extenuating_circumstances.data
        proj.area_list = form.area_list.data
        db.session.commit()
        flash('Project Updated Successfully!', 'success')
        return redirect(url_for('home'))  
    elif request.method == 'GET':
        form.name.data = proj.name
        form.site_id.data = Site.query.get(proj.site_id)
        form.status_id.data = Status.query.get(proj.status.id)
        form.typeOfWork_id.data = Worktype.query.get(proj.typeOfWork_id)
        form.description.data = proj.description 
        form.date_start.data = proj.date_start
        form.target_end_date.data = proj.target_end_date 
        form.hours_estimate.data = proj.hours_estimate 
        form.quote_amt.data = proj.quote_amt 
        form.damage_comment.data = proj.damage_comment
        form.extenuating_circumstances.data = proj.extenuating_circumstances

        form.area_list.data = proj.area_list.filter_by(site_id=proj_site_id)
    return render_template('update_project.html', title='Update Project', 
                            form=form, legend='Update Project', site=site, proj=proj)


# Filter by area
@app.route("/projects/<int:cur_proj_id>/areafilter", methods=['GET', 'POST'])
def area_filter(cur_proj_id):
    proj = Project.query.get_or_404(cur_proj_id) # Get Project from url
    site = Site.query.get(proj.site_id) # get site of project
    # This is a drop down filter showing all areas in given site.
    filterForm = AreaFilterForm()
    filterForm.areas.query = Area.query.filter_by(site_id=proj.site_id)

    if filterForm.validate_on_submit():
        selected_area_id = filterForm.areas.data.id
        flash('Area Filter Applied', 'success')
        return redirect(url_for('add_room_to_project', 
                        title='Add Rooms to a Projects', 
                        legend='Add Rooms to a Project',                # Drop filterForm?
                        selected_area_id=selected_area_id, proj=proj, filterForm=filterForm,
                        site=site, cur_proj_id=cur_proj_id))
    
    return render_template('area_filter.html', title='Add Rooms to a Project', 
                            legend='Select Area to filter by', cur_proj_id=cur_proj_id,
                            site=site, filterForm=filterForm, proj=proj)

# Add room to project
@app.route("/projects/<int:cur_proj_id>/<int:selected_area_id>", methods=['GET', 'POST'])
def add_room_to_project(cur_proj_id, selected_area_id):
    # At this point results are limited to those in the selected Area
    proj = Project.query.get_or_404(cur_proj_id) # Get Project from url
    site = Site.query.get(proj.site_id) # get site of project
    area = Area.query.filter_by(id=selected_area_id).first()
    #  
    form = AddRoomToProjectForm() 
    # Apply filter to query object
    form.room_list.query = Room.query.filter_by(area_id=selected_area_id)
    rooms_in_proj = proj.room_list.all()
    if form.validate_on_submit(): # Add selected rooms to project_room table
        # First check if the room is already in the list
        # Iterate through rooms in form
        for room in form.room_list.data:
            if room not in rooms_in_proj:
                proj.room_list.append(room)
            
            # Remove previous rooms
            if room not in form.room_list.data :
                proj.room_list.remove(room)
            # IF form room is NOT in room, add it.
            if room not in proj.room_list.all():
                proj.room_list.append(room)
        db.session.commit()
        flash('Rooms added to Project', 'success')
        return redirect(url_for('project_list'))

    elif request.method == 'GET':
        form.room_list.data = proj.room_list

    return render_template('add_room_to_project.html', title='Add Rooms to a Project', 
                            legend='Select Rooms to Add', selected_area_id=selected_area_id,
                            site=site, form=form, proj=proj, area=area)



# Display all Areas in the chosen site
@app.route("/site/<int:cur_site_id>")
def site_area_list(cur_site_id):
    site = Site.query.get_or_404(cur_site_id) # get current site from the site_id in url
    areas = Area.query.filter_by(site_id=site.id).order_by(Area.name).all()
    
    # Save the starting directory
    startDir = os.getcwd()
    # change to static/area_color_sheets
    cs_dir = os.path.join(app.root_path, 'static/area_color_sheets')
    os.chdir(cs_dir)

    for area in areas:
        cs_list = area.color_sheets
        for cs in cs_list:
            cs_fn = cs.name
            cs_path = os.path.join(app.root_path, 'static/area_color_sheets', cs_fn)
        
            # check if it is on local file system
            if not os.path.isfile(cs_path):
                # If the color sheet isn't stored locally,
                # go and download it from amazon S3 bucket
                download_file(cs_fn, bucket, cs_fn)
                print('downloaded ' + str(cs_fn) + ' from AWS S3 Bucket')
    
    # return to the starting dir
    os.chdir(startDir)

    return render_template('areas_by_site.html', title='Area List', areas=areas, site=site)


# Save area picture
def save_area_picture(form_picture, area):
    area_code = area.code
    date_added = datetime.date(datetime.utcnow())
    random_hex = secrets.token_hex(1)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = area_code + "-" + str(date_added) + "-" + random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/area_color_sheets', picture_fn)

    i = Image.open(form_picture)

    i.save(picture_path)

    return picture_fn, picture_path

# Update area details; Use to Add a color sheet to an area
@app.route("/site/<int:cur_site_id>/<int:cur_area_id>/update", methods=['GET', 'POST'])
@login_required
def update_area(cur_site_id, cur_area_id):
    site = Site.query.get_or_404(cur_site_id) # Get current site_id from URL
    area = Area.query.get_or_404(cur_area_id) # Get current area_id
    form = UpdateAreaForm()
    if form.validate_on_submit():
        if form.color_sheet.data:
            print("color_sheet has data")
            picture_file, picture_path = save_area_picture(form.color_sheet.data, area)
            print("filename:" + picture_file)

            # Define the S3 Bucket
            upload_file(picture_path, bucket, picture_file)

            # Create the entry into the ColorSheet Table
            cs=ColorSheet(area_id=area.id, name=picture_file)
            db.session.add(cs)
            area.color_sheets.append(cs)
            area.color_sheet = picture_file
            print("Picture saved")
        # Check for form data AND that it is different than the current area.site_id
        if(form.site_id.data and form.site_id.data != area.site_id):
            updated_site = Site.query.filter_by(id=form.site_id.data.id).first()
            area.site_id = updated_site.id
        area.name = form.name.data
        area.code = form.code.data
        area.building = form.building.data
        area.level = form.level.data
        area.descriptor = form.descriptor.data
        db.session.commit()
        flash('The Area has been updated!', 'success')
        return redirect(url_for('site_list'))
    elif request.method == 'GET':
        # site_id was blank when loading page, despite being set below...
        form.site_id.data = Site.query.get(area.site_id)
        form.name.data = area.name
        form.code.data = area.code
        form.building.data = area.building
        form.level.data = area.level
        form.descriptor.data = area.descriptor
    # add color_sheet so it displays?
    # color_sheet = url_for('static', filename='area_color_sheets/' + area.color_sheet)
    return render_template('update_area.html', title='Update Area',
                           form=form, legend='Update Area', site=site, area=area)


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)

# View all sites
@app.route("/site")
def site_list():
    sites = Site.query.all()
    return render_template('site_list.html', title='Site List', sites=sites)


# View all Rooms in the chosen Area
@app.route("/site/<int:cur_site_id>/<int:cur_area_id>")
def area_room_list(cur_site_id, cur_area_id):
    site = Site.query.get_or_404(cur_site_id) # get current site from the site_id in url
    area = Area.query.get_or_404(cur_area_id) # get current area from the area_id in url
    rooms = Room.query.filter_by(area_id=area.id).all()
    return render_template('rooms_by_area.html', title='Room List', rooms=rooms, area=area, site=site)

# Add new site
@app.route("/site/new", methods=['GET', 'POST'])
def new_site():
    form = NewSiteForm()
    if form.validate_on_submit():
        site = Site(name=form.name.data, code=form.code.data, addr_str=form.addr_str.data, city=form.city.data)
        db.session.add(site)
        db.session.commit()
        flash('A new Site has been created!', 'success')
        return redirect(url_for('site_list'))
    return render_template('new_site.html', title='Add New Site',
                             form=form, legend='Add New Site')


# Add new Area to the chosen Site
@app.route("/site/<int:cur_site_id>/new", methods=['GET', 'POST'])
def add_area(cur_site_id):
    site = Site.query.get_or_404(cur_site_id)
    form = NewAreaForm()
    if form.validate_on_submit():
        area = Area(name=form.name.data, 
                    code=form.code.data, 
                    site_id=site.id, 
                    building=form.building.data, 
                    level=form.level.data, 
                    descriptor=form.descriptor.data)
        db.session.add(area)
        db.session.commit()
        flash('New Area Added Successfully!', 'success')
        return redirect(url_for('site_area_list', cur_site_id=site.id))   
    return render_template('add_area_to_site.html', title='Add New Area', site=site, form=form)

# Add a new Area
@app.route("/newArea", methods=['GET', 'POST'])
def new_area():
    form = NewAreaForm()
    if form.validate_on_submit():
        area = Area(name=form.name.data, code=form.code.data, site_id=form.site_id.data.id, building=form.building.data, level=form.level.data, descriptor=form.descriptor.data)
        db.session.add(area)
        db.session.commit()
        flash('New Area Added Successfully!', 'success')
        return redirect(url_for('home'))   
    return render_template('new_area.html', title='Add New Area', form=form, legend='Add a New Area')

# Add a new Room
@app.route("/newRoom", methods=['GET', 'POST'])
def new_room():
    form = NewRoomForm()
    if form.validate_on_submit():
        room = Room(bm_id=form.bm_id.data, name=form.name.data, area_id=form.area_id.data.id)
        db.session.add(room)
        db.session.commit()
        flash('New Room Added Successfully!', 'success')
        return redirect(url_for('home'))   
    return render_template('new_room.html', title='Add New Room', form=form, legend='Add a New Room')

# Basic about page, shows my intentions for the site going forward
@app.route("/about")
def about():
    return render_template('about.html', title='About')

# Register a new user
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# Login with existing credentials
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

# Logout
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

# Save profile thumbnail
def save_thumbnail(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


# Update Account form
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_thumbnail(form.picture.data)
            print("filename: " + picture_file)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.fName.data = current_user.fName
        form.lName.data = current_user.lName
        form.cellPhone.data = current_user.cellPhone
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


# Reset Password Request

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', 
                  sender='ultrapaintdb@gmail.com', 
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link: 
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated. You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)

#########################################################
############### BEGIN PaintBuilder Routes ###############
#########################################################

# Add a new Supplier
@app.route("/newsupplier", methods=['GET', 'POST'])
def add_supplier():
    form=NewSupplierForm()
    if form.validate_on_submit():
        newSupplier = Supplier(name=form.name.data, addr_str=form.addr_str.data, city=form.city.data)
        db.session.add(newSupplier)
        db.session.commit()
        flash('New Supplier Added Successfully!', 'success')
        return redirect(url_for('paint_builder'))
    return render_template('add_supplier.html', title='Add a New Supplier', legend='Add a New Supplier', form=form)

# Add a new Brand
@app.route("/newbrand", methods=['GET', 'POST'])
def add_brand():
    form=NewBrandForm()
    form.supplier.query = Supplier.query
    if form.validate_on_submit():
        newBrand = Brand(name=form.name.data, supplier_id=form.supplier.data.id)
        db.session.add(newBrand)
        db.session.commit()
        # Add brand to supplier?

        flash('New Brand Added Successfully!', 'success')
        return redirect(url_for('paint_builder'))
    if request.method == 'GET':
        form.supplier.data = Supplier.query.first()
    return render_template('add_brand.html', title='Add a New Brand', legend='Add a New Brand', form=form)

# Add a new Product
@app.route("/newproduct", methods=['GET', 'POST'])
def add_product():
    form=NewProductForm()
    form.brand.query = Brand.query
    if form.validate_on_submit():
        newProduct = Product(name=form.name.data, brand_id=form.brand.data.id)
        db.session.add(newProduct)
        db.session.commit()
        flash('New Product Added Successfully!', 'success')
        return redirect(url_for('paint_builder'))
    if request.method == 'GET':
        form.brand.data = Brand.query.first()
    return render_template('add_product.html', title='Add a New Product', legend='Add a New Product', form=form)

# Add a new Color
@app.route("/newcolor", methods=['GET', 'POST'])
def add_color():
    form=NewColorForm()
    if form.validate_on_submit():
        newColor = Color(name=form.name.data, code=form.code.data)
        db.session.add(newColor)
        db.session.commit()
        flash('New Color Added Successfully!', 'success')
        return redirect(url_for('paint_builder'))
    return render_template('add_color.html', title='Add a New Color', legend='Add a New Color', form=form)


# Create a new PaintColor
@app.route("/paintBuilder", methods=['GET', 'POST'])
def paint_builder():
    form = PaintColorBuilderForm()
    form.supplier.query = Supplier.query
    form.brand.query = Brand.query
    form.product.query = Product.query
    form.sheen.query = Sheen.query
    form.color.query = Color.query
    if form.validate_on_submit():
        # Add Paint to db
        paint = Paint(supplier_id= form.supplier.data.id, 
                      brand_id= form.brand.data.id, 
                      product_id= form.product.data.id, 
                      sheen_id= form.sheen.data.id)
        db.session.add(paint)
        db.session.commit()
        # Add PaintColor to db
        paintcolor = PaintColor(paint_id=paint.id, 
                                color_id=form.color.data.id,
                                prod_code= form.prod_code.data,
                                base= form.base.data,
                                formula= form.formula.data)
        db.session.add(paintcolor)
        db.session.commit()
        flash('New PaintColor Added Successfully!', 'success')
        return redirect(url_for('home'))
    if request.method=='GET':
        # Set the intial values for the dropdown boxes
        form.supplier.data = ' '
        # # limit the Brands and Products to those of the selected supplier.
        # # This is best (only) done with AJAX or JQuery
        # form.brand.data = Brand.query.first()
        # form.product.data = Product.query.first()
        # form.sheen.data = Sheen.query.first()
        # form.color.data = Color.query.first()
    return render_template('paint_builder.html', title='Create a New PaintColor', legend='Create a New PaintColor', form=form)

#########################################################
###################### JSON Routes ######################
#########################################################
@app.route("/getbrands/<supplier>")
def brand(supplier):
    # Get all brands for the given supplier
    brands = Brand.query.filter_by(supplier_id=supplier).all()
    # Create an empty list
    brandArray = []
    # go through returned brands and append as obj to list
    for brand in brands:
        brandObj = {}
        brandObj['id'] = brand.id 
        brandObj['name'] = brand.name  
        brandArray.append(brandObj)
    # Return 'brands' of given supplier as json data
    return jsonify({'brands' : brandArray})

@app.route("/getproducts/<brand>")
def product(brand):
    # Get all products for the given brand
    products = Product.query.filter_by(brand_id=brand).all()
    # Create an empty list
    productArray = []
    # go through returned products and append as obj to list
    for product in products:
        productObj = {}
        productObj['id'] = product.id 
        productObj['name'] = product.name  
        productArray.append(productObj)
    # Return 'products' of given brand as json data
    return jsonify({'products' : productArray})

@app.route("/getareas/<site>")
def area(site):
    # Get all areas for the given site
    areas = Area.query.filter_by(site_id=site).all()
    # Create an empty list
    areaArray = []
    # go through returned products and append as obj to list
    for area in areas:
        areaObj = {}
        areaObj['id'] = area.id 
        areaObj['name'] = area.name  
        areaArray.append(areaObj)
    # Return 'products' of given brand as json data
    return jsonify({'areas' : areaArray})


#########################################################
#################### END JSON Routes ####################
#########################################################


#########################################################
################ END PaintBuilder Routes ################
#########################################################