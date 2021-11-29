from os import environ, path
from python_dotenv import dotenv

load_dotenv()

SECRET_KEY = environ.get('SECRET_KEY')
FLASK_ENV = environ.get('FLASK_ENV')

# Database
SQLALCHEMY_DATABASE_URI = environ['DATABASE_URL']
SQLALCHEMY_ECHO = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-Security Configs
SECURITY_PASSWORD_SALT = environ['SECURITY_SALT']
SECURITY_CONFIRMABLE = True
SECURITY_REGISTERABLE = True
SECURITY_TRACKABLE = True
SECURITY_POST_LOGIN_VIEW = '/about'
SECURITY_POST_LOGOUT_VIEW = '/home'
SECURITY_POST_REGISTER_VIEW = '/about'
SECURITY_RESET_PASSWORD_WITHIN = '1 hours'
SECURITY_CONFIRM_EMAIL_WITHIN = '24 hours'
SECURITY_RECOVERABLE = True

# Flask-Mail Configs
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'noreply.fluffybunny@gmail.com'
MAIL_PASSWORD = environ['MAIL_PASSWORD']
MAIL_DEFAULT_SENDER = ('Fluffy Bunny Admins', 'noreply.fluffybunny@gmail.com')
MAIL_MAX_EMAILS = 5
MAIL_SUPPRESS_SEND = False
MAIL_ASCII_ATTACHMENTS = False
MAIL_DEBUG = False

# Flask-Admin Configs
FLASK_ADMIN_SWATCH = 'sandstone'
