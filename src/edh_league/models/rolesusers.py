from src.edh_league.sqla import sqla


class RolesUsers(sqla.Model):
    id = sqla.Column(sqla.Integer, primary_key=True, autoincrement=True)
    user_id = sqla.Column(sqla.Integer, sqla.ForeignKey('admin.users.id'))
    role_id = sqla.Column(sqla.Integer, sqla.ForeignKey('admin.roles.id'))
