from src.edh_league.sqla import sqla


class UserCommander(sqla.Model):
    id = sqla.Column(sqla.Integer, primary_key=True, autoincrement=True)
    user_id = sqla.Column(sqla.Integer, sqla.ForeignKey('admin.users.id'))
    commander_id = sqla.Column(sqla.Integer, sqla.ForeignKey('admin.commanders.id'))
