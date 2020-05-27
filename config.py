import os

basedir = os.path.abspath(os.path.dirname(__file__))

# define the S3 bucket name for the color sheets
colorSheetBucket = 'upaintdb-colorsheets'

class Config(object):
    # UnComment top to run off local
    # SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:SQLftw99@localhost:5432/UPaintDB'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('LOCAL_POSTGRES_URL') or \
    #     'sqlite:///' + os.path.join(basedir, 'site.db') 
    # This is the local connection string 'postgresql://postgres:SQLftw99@localhost:5432/UPaintDB'
    
    # Comment out the above and Uncomment below here before uploading to Heroku
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or '5781628bb0b13ce0c686dfde281ba245'
    # flask-Mail variables
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')

    