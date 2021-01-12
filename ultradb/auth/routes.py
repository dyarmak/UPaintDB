from flask import Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from ultradb.auth.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from ultradb.models import User
from flask import render_template, url_for, flash, redirect, request
from ultradb import db, bcrypt

from ultradb.auth.utils import save_thumbnail, send_reset_email, send_welcome_email, roleAuth

auth_bp = Blueprint('auth_bp', __name__)


# Register a new user
@auth_bp.route("/register", methods=['GET', 'POST'])
@login_required
def register():
    # Must be Admin
    if not roleAuth('Admin'):
        return redirect(url_for('main_bp.home'))

    form = RegistrationForm()
    # We will set a temp password for the new user
    defaultPass = "#Upa1ntDBT3mp$"

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(defaultPass).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, fName=form.fName.data, lName=form.lName.data)
        db.session.add(user)
        db.session.commit()
        flash('Account has been created! They are now able to log in', 'success')
        # Here we want to send an email letting them know their account has been created 
        # And ask them to please reset their password on login
        send_welcome_email(user)
        return redirect(url_for('main_bp.home'))
    return render_template('register.html', title='Register a new User', form=form)

# Login with existing credentials
@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main_bp.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

# Logout
@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main_bp.home'))


# Update Account form
@auth_bp.route("/account", methods=['GET', 'POST'])
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
        return redirect(url_for('auth_bp.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.fName.data = current_user.fName
        form.lName.data = current_user.lName
        form.cellPhone.data = current_user.cellPhone
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@auth_bp.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('auth_bp.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@auth_bp.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth_bp.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated. You are now able to log in', 'success')
        return redirect(url_for('auth_bp.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
