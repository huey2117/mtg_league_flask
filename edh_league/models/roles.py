from sqlalchemy.orm import validates

from edh_league.sqla import sqla


class Roles(sqla.Model):
    id = sqla.Column(sqla.Integer, primary_key=True, autoincrement=True)
    name = sqla.Column(sqla.String(80), unique=True, nullable=False)
    description = sqla.Column(sqla.String(255))
    users = sqla.relationship(
        'Users', secondary='admin.roles_users',
        backref=sqla.backref('admin.roles', lazy=True)
    )

    @validates('name')
    def validate_not_empty(self, key, value):
        if not value:
            raise ValueError(f'{key.capitalize} is required. ')
        return value

    def __repr__(self):
        return self.name
