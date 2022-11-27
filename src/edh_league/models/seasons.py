from src.edh_league.sqla import sqla


class Seasons(sqla.Model):
    id = sqla.Column(sqla.Integer, primary_key=True, autoincrement=True)
    name = sqla.Column(sqla.String(64))
    start_date = sqla.Column(sqla.Date())
    num_games = sqla.Column(sqla.Integer)
    is_current = sqla.Column(sqla.Boolean)
    winner_user_id = sqla.Column(sqla.Integer)

