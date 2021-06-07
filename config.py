from os import environ, path

SECRET_KEY = environ.get('SECRET_KEY')
FLASK_ENV = environ.get('FLASK_ENV')

# Database
SQLALCHEMY_DATABASE_URI = environ['DATABASE_URL']
SQLALCHEMY_ECHO = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-Security Configs
SECURITY_PASSWORD_SALT = b'8\xc3\xe5\xb2\xce=\x0f\xceF\xeat\xaf\xfb|\x8b\x961\xc2$:\x07\t*o\x7f\xdb\xa7\x06\xd2![sr\xc0\xf8{l\rgs\x89"\xd8\xed\x8a\x8dN\xc1\xb2\xb7\xc5\x81\x14k2\xd6a\xf7\xbfv\x13\xb0\x1a\x8c\xbf\xb5\x00\xd7Q\x16\x92\xa9]\x06\xfe\xe4\xfe\xc3\x93\x84\xa7\xc0\xc9Tok2\xf8\xeb\xc6\xeb\xe0o\xca[\xab\x8ckZ\xe0\xd62k\x8b\x0ba\xba\x88\xc9\n\x98U\xcfL9\x87\xc4l\xbb\x8e\x83?\x14\x00\xc22V\xca'
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
