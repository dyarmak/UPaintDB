# Utility functions

import os
import os.path
import secrets
from ultradb import mail
from flask_mail import Message
from flask import current_app, url_for
from PIL import Image

# Save profile thumbnail
def save_thumbnail(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


# Reset Password Request
def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', 
                  sender='ultrapaintdb@gmail.com', 
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link: 
{url_for('auth_bp.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


# Welcome to UpaintDB email
def send_welcome_email(user):
    msg = Message('Welcome to UPaintDB', 
                  sender='ultrapaintdb@gmail.com', 
                  recipients=[user.email])
    msg.body = f'''Welcome to UPaintDB! 

You will need to use this site to submit your hours for payroll.

To log in, please visit the following link to set your password:
{url_for('auth_bp.reset_request', _external=True)}

Thank you,
UPaintDB
'''
    mail.send(msg)