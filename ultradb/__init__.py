from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_talisman import Talisman, GOOGLE_CSP_POLICY


mail = Mail()
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth_bp.login'
login_manager.login_message_category = 'info'
talisman = Talisman()



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    mail.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)


    csp = {
        'default-src': [
            '\'self\'',
            '\'unsafe-inline\'',
            '*.gstatic.com'
        ],
        'font-src': [
                '\'self\'',
                'themes.googleusercontent.com',
                '*.gstatic.com'
        ],
        'frame-src': [
                '\'self\'',
                'www.google.com',
                'www.youtube.com'
        ],
        'script-src':[
                '\'self\'', 
                '\'unsafe-eval\'',
                '\'unsafe-inline\'',
                'data:',
                'code.jquery.com',
                'cdnjs.cloudflare.com',
                'maxcdn.bootstrapcdn.com',
                'ajax.googleapis.com',
                'www.googleanalytics.com',
                'www.google-analytics.com',
                'https://www.googletagmanager.com',
                'https://www.google-analytics.com',
                'https://www.googletagmanager.com',
                'https://google-analytics.com',
                'https://tagmanager.google.com/'
        ],
        'style-src': [
                '\'self\'', 
                '\'unsafe-inline\'',
                'maxcdn.bootstrapcdn.com',
                'ajax.googleapis.com', 
                'fonts.googleapis.com', 
                '*.gstatic.com'
        ],
        'img-src': [
                    'data:', 
                    '\'self\'', 
                    'maxcdn.bootstrapcdn.com'],
        'object-src' : [
                    '\'self\''
        ]    }



    talisman.init_app(app, force_https=True, content_security_policy=csp)

    from ultradb.auth.routes import auth_bp
    from ultradb.main.routes import main_bp
    from ultradb.paints.routes import paint_bp
    from ultradb.posts.routes import post_bp
    from ultradb.projects.routes import project_bp
    from ultradb.sites.routes import site_bp
    from ultradb.timesheets.routes import timesheet_bp 
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(paint_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(site_bp)
    app.register_blueprint(timesheet_bp)

    return app

