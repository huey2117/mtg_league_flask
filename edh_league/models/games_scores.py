from edh_league.sqla import sqla


class GamesScores(sqla.Model):
    id = sqla.Column(sqla.Integer, primary_key=True, autoincrement=True)
    user_id = sqla.Column(sqla.Integer, sqla.ForeignKey('admin.users.id'))
    game_id = sqla.Column(sqla.Integer, sqla.ForeignKey('admin.games.id'))
    pts_total = sqla.Column(sqla.Integer)
    scores = sqla.Column(sqla.JSON())