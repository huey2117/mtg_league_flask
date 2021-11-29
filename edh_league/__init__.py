import os

from flask import Flask
from . import db
from . import auth
from edh_league.sqla import sqla
from flask_migrate import Migrate
from edh_league.login import login_manager


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    # TODO: UPDATE DATABASE
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'edh_league.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    # configure Flask-SQLAlchemy
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=f"{app.config['DATABASE_URI']}", SQLALCHEMY_TRACK_MODIFICATIONS=false)
    sqla.init_app(app)

    # configure Flask-Login
    login_manager.init_app(app)

    # configure Flask-Migrate
    Migrate(app, sqla)

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
