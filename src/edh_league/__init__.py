import os

from flask import Flask
from flask_migrate import Migrate

from src.edh_league.login import login_manager
from src.edh_league.sqla import sqla
from . import auth
from . import db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')
    app.config.from_mapping(
        SECRET_KEY=app.config['SECRET_KEY'],
        DATABASE=app.config['SQLALCHEMY_DATABASE_URI'],
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    db.init_app(app)

    # configure Flask-SQLAlchemy
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=f"{app.config['SQLALCHEMY_DATABASE_URI']}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False)
    sqla.init_app(app)

    # configure Flask-Login
    login_manager.init_app(app)

    # configure Flask-Migrate
    Migrate(app, sqla)

    app.register_blueprint(auth.bp)
    # app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
