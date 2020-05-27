from flask import current_app
from datetime import datetime
import secrets
import os.path
from PIL import Image

# Save area picture
def save_area_picture(form_picture, area):
    area_code = area.code
    date_added = datetime.date(datetime.utcnow())
    random_hex = secrets.token_hex(1)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = area_code + "-" + str(date_added) + "-" + random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/area_color_sheets', picture_fn)

    i = Image.open(form_picture)

    i.save(picture_path)

    return picture_fn, picture_path