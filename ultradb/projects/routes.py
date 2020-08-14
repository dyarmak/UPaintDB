from datetime import datetime
from flask import Blueprint, render_template, url_for, flash, redirect, request
from ultradb import db
from ultradb.projects.forms import NewProjectForm, UpdateProjectForm, AddRoomToProjectForm, AreaFilterForm, NewProjectSimpleForm
from ultradb.models import Site, Area, Room, Project, Status, Worktype, Client

from flask_login import current_user, login_required
from flask_mail import Message

from ultradb.auth.utils import roleAuth
from ultradb.projects.utils import check_status_change

project_bp = Blueprint('project_bp', __name__)


# View all projects (active projects filter?)
@project_bp.route("/projects")
@login_required
def project_list():
    projects = []
    # Should apply a couple of sorts here, we'll build the list in our custom order
    # First should be active projects, IE status_id=3
    active = Project.query.filter_by(status_id=3).all()
    for item in active:
        projects.append(item)
    # then Painting Complete, IE status_id=4
    paintComplete = Project.query.filter_by(status_id=4).all()
    for item in paintComplete:
        projects.append(item)
    # then we want to get the upcoming and quoted IE status_id = 1||2
    upcoming = Project.query.filter_by(status_id=1).all()
    for item in upcoming:
        projects.append(item)    
    
    quoted = Project.query.filter_by(status_id=2).all()
    for item in quoted:
        projects.append(item)
    # then paused, IE status_id=6
    paused = Project.query.filter_by(status_id=6).all()
    for item in paused:
        projects.append(item)

    # then invoiced, IE status_id=5, needs to be sorted by date completed
    invoiced = Project.query.filter_by(status_id=5).order_by(Project.date_finished.desc()).all()
    for item in invoiced:
        projects.append(item)

    # then finally cancelled, IE status_id=7
    cancelled = Project.query.filter_by(status_id=7).all()
    for item in cancelled:
        projects.append(item)
    # projects = Project.query.order_by(Project.status_id.desc()).all()

    return render_template('project_list.html', title='Project List', projects=projects)

@project_bp.route("/newprojectsimple", methods=['GET', 'POST'])
@login_required
def new_project_simple():
    # Must be Manager or greater
    if not roleAuth('Manager'):
        return redirect(url_for('main_bp.home'))
    
    form = NewProjectSimpleForm()
    if form.validate_on_submit():
        project = Project(name= form.name.data,
                          client_id=form.client_id.data.id,
                          site_id=form.site_id.data.id, 
                          status_id=form.status_id.data.id, 
                          typeOfWork_id=form.typeOfWork_id.data.id, 
                          description=form.description.data, 
                          date_start=form.date_start.data, 
                          damage_comment=form.damage_comment.data, 
                          extenuating_circumstances=form.extenuating_circumstances.data)
        db.session.add(project)
        db.session.commit()
        flash('New Project Added Successfully!', 'success')
        return redirect(url_for('main_bp.home'))   
    return render_template('project_new_simple.html', title='Add New Project', form=form, legend='Add a New Project')

# Add a new Project
@project_bp.route("/newproject", methods=['GET', 'POST'])
@login_required
def new_project():
    # Must be Admin
    if not roleAuth('Admin'):
        return redirect(url_for('main_bp.home'))

    form = NewProjectForm()
    if form.validate_on_submit():
        project = Project(name= form.name.data,
                          client_id=form.client_id.data.id,
                          site_id=form.site_id.data.id, 
                          status_id=form.status_id.data.id, 
                          typeOfWork_id=form.typeOfWork_id.data.id, 
                          description=form.description.data, 
                          date_start=form.date_start.data, 
                          target_end_date=form.target_end_date.data, 
                          hours_estimate= form.hours_estimate.data,
                        #   area_list= form.area_list.data,
                          quote_amt=form.quote_amt.data, 
                          damage_comment=form.damage_comment.data, 
                          extenuating_circumstances=form.extenuating_circumstances.data)
        db.session.add(project)
        db.session.commit()
        flash('New Project Added Successfully!', 'success')
        return redirect(url_for('main_bp.home'))   
    return render_template('project_new.html', title='Add New Project', form=form, legend='Add a New Project')


# View Project details
@project_bp.route("/projects/<int:cur_proj_id>")
@login_required
def view_project(cur_proj_id):
    # Must be employee
    if not roleAuth('Employee'):
        return redirect(url_for('main_bp.home'))

    # get basic project info to display
    proj = Project.query.get_or_404(cur_proj_id)
    if proj.client_id != None:
        client = Client.query.get(proj.client_id)
    else:
        client = None
    site = Site.query.get(proj.site_id)
    status = Status.query.get(proj.status_id)
    typeOfWork = Worktype.query.get(proj.typeOfWork_id)
    # Get list of areas in Project
    # areas = proj.area_list
    # Get list of rooms in Project
    rooms = proj.room_list
    # get list of Timesheets for Project
    tss = proj.timesheets.all()
    # Sum up the total hours for display
    total_hours = 0
    for ts in tss:
        total_hours += ts.hours

    return render_template('project_details.html', title='Project Info', legend='Project Info', 
                        proj=proj, site=site, status=status, typeOfWork=typeOfWork, 
                        # areas=areas, 
                        client=client, rooms=rooms, tss=tss, total_hours=total_hours)


# Update an existing Project, Add rooms and areas?
@project_bp.route("/projects/<int:cur_proj_id>/update", methods=['GET', 'POST'])
@login_required
def update_project(cur_proj_id):
    # Must be Admin
    if not roleAuth('Admin'):
        return redirect(url_for('main_bp.home'))


    proj = Project.query.get_or_404(cur_proj_id)
    proj_site_id = proj.site_id
    site = Site.query.get(proj_site_id)
    orig_status = proj.status_id
    form = UpdateProjectForm()  
    # This allows me to change the query and apply a filter to it for the page!
    # form.area_list.query = Area.query.filter_by(site_id=proj.site_id)
    if form.validate_on_submit():
        proj.name = form.name.data 
        proj.client_id = form.client_id.data.id
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
        # proj.area_list = form.area_list.data
        
        # Check if the project status has been changed and update accordingly
        check_status_change(proj, orig_status)

        # commit changes
        db.session.commit()
        flash('Project Updated Successfully!', 'success')
        return redirect(url_for('main_bp.home'))  
    elif request.method == 'GET':
        form.name.data = proj.name
        form.client_id.data = Client.query.get(proj.client_id)
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

        # form.area_list.data = proj.area_list.filter_by(site_id=proj_site_id)
    return render_template('project_update.html', title='Update Project', 
                            form=form, legend='Update Project', site=site, proj=proj)


# Update an existing Project, Add rooms and areas?
@project_bp.route("/projects/<int:cur_proj_id>/update_simple", methods=['GET', 'POST'])
@login_required
def update_project_simple(cur_proj_id):
    # Managers need to be able to add rooms to a project, but not see the admin fields.
    # Must be Manager
    if not roleAuth('Manager'):
        return redirect(url_for('main_bp.home'))


    proj = Project.query.get_or_404(cur_proj_id)
    orig_status = proj.status_id
    proj_site_id = proj.site_id
    site = Site.query.get(proj_site_id)
    form = UpdateProjectForm()  
    # This allows me to change the query and apply a filter to it for the page!
    # form.area_list.query = Area.query.filter_by(site_id=proj.site_id)
    if form.validate_on_submit():
        proj.name = form.name.data 
        proj.client_id = form.client_id.data.id
        proj.site_id = form.site_id.data.id
        proj.status_id = form.status_id.data.id
        proj.typeOfWork_id = form.typeOfWork_id.data.id
        proj.description = form.description.data
        proj.date_start = form.date_start.data
        proj.damage_comment = form.damage_comment.data
        proj.extenuating_circumstances = form.extenuating_circumstances.data
        # proj.area_list = form.area_list.data

        # Check if the project status has been changed and update accordingly
        check_status_change(proj, orig_status)

        db.session.commit()
        flash('Project Updated Successfully!', 'success')
        return redirect(url_for('main_bp.home'))  
    elif request.method == 'GET':
        form.name.data = proj.name
        form.client_id.data = Client.query.get(proj.client_id)
        form.site_id.data = Site.query.get(proj.site_id)
        form.status_id.data = Status.query.get(proj.status.id)
        form.typeOfWork_id.data = Worktype.query.get(proj.typeOfWork_id)
        form.description.data = proj.description 
        form.date_start.data = proj.date_start
        form.damage_comment.data = proj.damage_comment
        form.extenuating_circumstances.data = proj.extenuating_circumstances

        # form.area_list.data = proj.area_list.filter_by(site_id=proj_site_id)
    return render_template('project_update_simple.html', title='Update Project', 
                            form=form, legend='Update Project', site=site, proj=proj)


# Filter by area
@project_bp.route("/projects/<int:cur_proj_id>/areafilter", methods=['GET', 'POST'])
@login_required
def area_filter(cur_proj_id):
    # Must be Admin
    if not roleAuth('Manager'):
        return redirect(url_for('main_bp.home'))
    proj = Project.query.get_or_404(cur_proj_id) # Get Project from url
    site = Site.query.get(proj.site_id) # get site of project
    # This is a drop down filter showing all areas in given site.
    filterForm = AreaFilterForm()
    filterForm.areas.query = Area.query.filter_by(site_id=proj.site_id)

    if filterForm.validate_on_submit():
        selected_area_id = filterForm.areas.data.id
        flash('Area Filter Applied', 'success')
        return redirect(url_for('project_bp.add_room_to_project', 
                        title='Add Rooms to a Projects', 
                        legend='Add Rooms to a Project',                # Drop filterForm?
                        selected_area_id=selected_area_id, proj=proj, filterForm=filterForm,
                        site=site, cur_proj_id=cur_proj_id))
    
    return render_template('project_area_filter.html', title='Add Rooms to a Project', 
                            legend='Select Area to filter by', cur_proj_id=cur_proj_id,
                            site=site, filterForm=filterForm, proj=proj)

# Add room to project
@project_bp.route("/projects/<int:cur_proj_id>/<int:selected_area_id>", methods=['GET', 'POST'])
@login_required
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
        
        # Remove all rooms in selected area from proj.room_list
        # Get rooms in this area
        rooms_in_area = Room.query.filter_by(area_id=selected_area_id).all()
        # iterate over these rooms
        for room in rooms_in_area:
            # if that room is assoc with proj, remove it
            if room in proj.room_list:
                proj.room_list.remove(room)
        
        # Then go through and add those that were selected.
        for room in form.room_list.data:
            proj.room_list.append(room)
        db.session.commit()
        
        flash('Rooms added to Project', 'success')
        return redirect(url_for('project_bp.project_list'))

    elif request.method == 'GET':
        form.room_list.data = proj.room_list

    return render_template('project_add_room.html', title='Add Rooms to a Project', 
                            legend='Select Rooms to Add', selected_area_id=selected_area_id,
                            site=site, form=form, proj=proj, area=area)
