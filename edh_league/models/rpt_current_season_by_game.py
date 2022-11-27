from edh_league.sqla import sqla


class RptCurrSeasonByGame(sqla.Model):
    user_id = sqla.Column(sqla.Integer, sqla.ForeignKey('admin.users.id'))
    games = sqla.Column(sqla.JSON())
    first_bloods = sqla.Column(sqla.Integer)
    first_places = sqla.Column(sqla.Integer)
    second_places = sqla.Column(sqla.Integer)
    third_places = sqla.Column(sqla.Integer)
    fourth_places = sqla.Column(sqla.Integer)