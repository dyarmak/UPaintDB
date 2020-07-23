import os
import os.path
from flask import Blueprint, render_template, url_for, redirect, request, flash, current_app, jsonify
from ultradb.sites.forms import UpdateAreaForm, NewSiteForm, NewAreaForm, RoomForm, NewClientForm
from ultradb.models import Site, Area, Room, ColorSheet, Client
from ultradb.sites.utils import save_area_picture
from flask_login import login_required
from s3funcs import upload_file, download_file
from supfuncs import build_upcomingDF, build_asneededDF
from ultradb import db
from config import colorSheetBucket


site_bp = Blueprint('site_bp', __name__)



@site_bp.route("/client")
def client_list():
    clients = Client.query.all()
    return render_template('client_list.html', title="Client List", clients=clients)


# ***************** #
# ** View Routes **
# ***************** #

# View all sites
@site_bp.route("/site")
def site_list():
    sites = Site.query.all()
    return render_template('site_list.html', title='Site List', sites=sites)

# Display all Areas in the chosen site
@site_bp.route("/site/<int:cur_site_id>")
def site_area_list(cur_site_id):
    site = Site.query.get_or_404(cur_site_id) # get current site from the site_id in url
    areas = Area.query.filter_by(site_id=site.id).order_by(Area.name).all()
    
    # Save the starting directory
    startDir = os.getcwd()
    # change to static/area_color_sheets
    cs_dir = os.path.join(current_app.root_path, 'static/area_color_sheets')
    os.chdir(cs_dir)

    for area in areas:
        cs_list = area.color_sheets
        for cs in cs_list:
            cs_fn = cs.name
            cs_path = os.path.join(current_app.root_path, 'static/area_color_sheets', cs_fn)
        
            # check if it is on local file system
            if not os.path.isfile(cs_path):
                # If the color sheet isn't stored locally,
                # go and download it from amazon S3 bucket
                download_file(cs_fn, colorSheetBucket, cs_fn)
                print('downloaded ' + str(cs_fn) + ' from AWS S3 Bucket')
    
    # return to the starting dir
    os.chdir(startDir)

    return render_template('site_area_list.html', title='Area List', areas=areas, site=site)

# View all Rooms in the chosen Area
@site_bp.route("/site/<int:cur_site_id>/<int:cur_area_id>")
def area_room_list(cur_site_id, cur_area_id):
    site = Site.query.get_or_404(cur_site_id) # get current site from the site_id in url
    area = Area.query.get_or_404(cur_area_id) # get current area from the area_id in url
    rooms = Room.query.filter_by(area_id=area.id).all()
    return render_template('rooms_by_area.html', title='Room List', rooms=rooms, area=area, site=site)


# ******************* #
# ** Update Routes **
# ******************* #

#update room details; Use to change date of last paint directly (hopefully not used often.)
@site_bp.route("/site/<int:cur_site_id>/<int:cur_area_id>/<int:cur_room_id>")
def room_update(cur_site_id, cur_area_id, cur_room_id):
    # We don't really need the site or area for this...
    site = Site.query.get_or_404(cur_site_id) # get current site from the site_id in url
    area = Area.query.get_or_404(cur_area_id) # get current area from the area_id in url
    room = Room.query.get_or_404(cur_room_id) # get the room for editting

    form = RoomForm()

    if form.validate_on_submit():
        room.bm_id = form.bm_id.data 
        room.name = form.name.data 
        room.location = form.location.data
        room.description = form.description.data
        room.date_last_paint = form.date_last_paint.data
        room.freq = form.freq.data
        room.site_id = form.site_id.data.id
        room.area_id = form.area_id.data.id
        room.glaccount = form.glaccount.data
        db.session.commit()
        flash('The Room has been updated!', 'success')
        return redirect(url_for('site_bp.area_room_list', cur_site_id=cur_site_id, cur_area_id=cur_area_id))
    elif request.method == 'GET':
        form.bm_id.data = room.bm_id
        form.name.data = room.name
        form.location.data = room.location
        form.description.data = room.description
        form.site_id.data = Site.query.get(room.site_id)
        form.area_id.data = Area.query.get(room.area_id)
        form.freq.data = room.freq
        form.date_last_paint.data = room.date_last_paint
        form.glaccount.data = room.glaccount
    return render_template('room_update.html', title='Update Room',  legend='Update Room Info',room=room, area=area, site=site, form=form)


# Update area details; Use to Add a color sheet to an area
@site_bp.route("/site/<int:cur_site_id>/<int:cur_area_id>/update", methods=['GET', 'POST'])
@login_required
def area_update(cur_site_id, cur_area_id):
    site = Site.query.get_or_404(cur_site_id) # Get current site_id from URL
    area = Area.query.get_or_404(cur_area_id) # Get current area_id
    form = UpdateAreaForm()
    if form.validate_on_submit():
        if form.color_sheet.data:
            print("color_sheet has data")
            picture_file, picture_path = save_area_picture(form.color_sheet.data, area)
            print("filename:" + picture_file)

            # Define the S3 Bucket
            upload_file(picture_path, colorSheetBucket, picture_file)

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
        return redirect(url_for('site_bp.site_list'))
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
    return render_template('area_update.html', title='Update Area',
                           form=form, legend='Update Area', site=site, area=area)

# ************************** #
# Routes for viewing Rooms
# ************************** #

# Display list of rooms in a site where date_next_paint <=1 year from today
@site_bp.route("/site/<int:cur_site_id>/upcoming")
def upcoming(cur_site_id):
    site = Site.query.get_or_404(cur_site_id)
    site_id = site.id
    name = site.name

    if site_id not in [1,2,5]:
        flash('We do not have a schedule for ' + name, 'warning')
        return redirect(url_for('site_bp.site_area_list', cur_site_id=site_id)) 


    upcoming_rooms = build_upcomingDF(site_id)
    
    return render_template('site_upcoming.html', tables=[upcoming_rooms.to_html(classes='data')], titles=upcoming_rooms.columns.values, title='Upcoming Rooms', legend='Upcoming Rooms', site=site)


# Display list of rooms in a site where freq = -1 or "as needed"
@site_bp.route("/site/<int:cur_site_id>/as_needed")
def as_needed(cur_site_id):
    site = Site.query.get_or_404(cur_site_id)
    site_id = site.id
    name = site.name
    
    if site_id not in [1,2,5]:
        flash('We do not have a schedule for ' + name, 'warning')
        return redirect(url_for('site_bp.site_area_list', cur_site_id=site_id)) 

    as_needed_rooms = build_asneededDF(site_id)

    return render_template('site_as_needed.html', tables=[as_needed_rooms.to_html(classes='data')], titles=as_needed_rooms.columns.values, title='As Needed Rooms', legend='As Needed Rooms', site=site)


# ************************************** #
# Routes for adding a new ____
# ************************************** #

# Add new Client
@site_bp.route("/client/new", methods=['GET', 'POST'])
def new_client():
    form = NewClientForm()
    if form.validate_on_submit():
        client = Client(name=form.name.data, contactName=form.contactName.data, contactEmail=form.contactEmail.data, contactPhone=form.contactPhone.data)
        db.session.add(client)
        db.session.commit()
        flash('A new Client has been created!', 'success')
        return redirect(url_for('site_bp.client_list'))
    return render_template('client_new.html', title='Add New Client',
                             form=form, legend='Add New Client')

# Add new site
@site_bp.route("/site/new", methods=['GET', 'POST'])
def new_site():
    form = NewSiteForm()
    if form.validate_on_submit():
        site = Site(name=form.name.data, code=form.code.data, addr_str=form.addr_str.data, city=form.city.data)
        db.session.add(site)
        db.session.commit()
        flash('A new Site has been created!', 'success')
        return redirect(url_for('site_bp.site_list'))
    return render_template('site_new.html', title='Add New Site',
                             form=form, legend='Add New Site')

# Add a new Area
@site_bp.route("/newArea", methods=['GET', 'POST'])
def new_area():
    form = NewAreaForm()
    if form.validate_on_submit():
        area = Area(name=form.name.data, code=form.code.data, site_id=form.site_id.data.id, building=form.building.data, level=form.level.data, descriptor=form.descriptor.data)
        db.session.add(area)
        db.session.commit()
        flash('New Area Added Successfully!', 'success')
        return redirect(url_for('main_bp.home'))   
    return render_template('area_new.html', title='Add New Area', form=form, legend='Add a New Area')

# Add new Area to the chosen Site
@site_bp.route("/site/<int:cur_site_id>/new", methods=['GET', 'POST'])
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
        return redirect(url_for('site_bp.site_area_list', cur_site_id=site.id))   
    return render_template('add_area_to_site.html', title='Add New Area', site=site, form=form)

# Add a new Room
@site_bp.route("/newRoom", methods=['GET', 'POST'])
def new_room():
    form = RoomForm()
    if form.validate_on_submit():
        room = Room(bm_id=form.bm_id.data, 
                    name=form.name.data, 
                    location=form.location.data,
                    description=form.description.data,
                    date_last_paint=form.date_last_paint.data,
                    freq=form.freq.data,
                    site_id=form.site_id.data.id,
                    area_id=form.area_id.data.id,
                    glaccount=form.glaccount.data)
        db.session.add(room)
        db.session.commit()
        flash('New Room Added Successfully!', 'success')
        return redirect(url_for('main_bp.home'))   
    return render_template('room_new.html', title='Add New Room', form=form, legend='Add a New Room')

@site_bp.route("/getareas/<site_id>")
def areasJson(site_id):
    # Get all brands for the given supplier
    areas = Area.query.filter_by(site_id=site_id).all()
    # Create an empty list
    areaArray = []
    # go through returned brands and append as obj to list
    for area in areas:
        areaObj = {}
        areaObj['id'] = area.id 
        areaObj['name'] = area.name  
        areaArray.append(areaObj)
    # Return 'brands' of given supplier as json data
    return jsonify({'areas' : areaArray})