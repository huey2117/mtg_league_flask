from uuid import uuid4

from flask_login import UserMixin
from sqlalchemy.orm import validates

from src.edh_league.login import login_manager
from src.edh_league.sqla import sqla


class Users(UserMixin, sqla.Model):
    id = sqla.Column(sqla.Integer, primary_key=True, autoincrement=True)
    uuid = sqla.Column(sqla.String, nullable=False,
                       default=lambda: str(uuid4()))
    email = sqla.Column(sqla.String(255), unique=True, nullable=False)
    first_name = sqla.Column(sqla.String(255))
    username = sqla.Column(sqla.String(255), nullable=False, unique=True)
    password = sqla.Column(sqla.String(255), nullable=False)
    last_login_at = sqla.Column(sqla.DateTime)
    current_login_at = sqla.Column(sqla.DateTime)
    last_login_ip = sqla.Column(sqla.String(100))
    current_login_ip = sqla.Column(sqla.String(100))
    login_count = sqla.Column(sqla.Integer)
    active = sqla.Column(sqla.Boolean)
    confirmed_at = sqla.Column(sqla.DateTime)
    roles = sqla.relationship(
        'Roles', secondary='admin.roles_users',
        backref=sqla.backref('admin.users', lazy=True)
    )

    @validates('email', 'password', 'username')
    def validate_not_empty(self, key, value):
        if not value:
            raise ValueError(f'{key.capitalize} is required. ')
        return value

    def get_id(self):
        return self.uuid

    def __repr__(self):
        return self.username


@login_manager.user_loader
def load_user(user_uuid):
    return Users.query.filter_by(uuid=user_uuid).first()
