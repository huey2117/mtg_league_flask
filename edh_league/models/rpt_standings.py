from edh_league.sqla import sqla


class RptStandings(sqla.Model):
    user_id = sqla.Column(sqla.Integer, sqla.ForeignKey('admin.users.id'))
    pts_total = sqla.Column(sqla.Integer)
    place_last_game = sqla.Column(sqla.Integer)
    pts_last_game = sqla.Column(sqla.Integer)