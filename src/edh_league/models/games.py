from src.edh_league.sqla import sqla


class Games(sqla.Model):
    id = sqla.Column(sqla.Integer, primary_key=True, autoincrement=True)
    season_id = sqla.Column(sqla.Integer, sqla.ForeignKey('admin.seasons.id'), nullable=False)
    game_num = sqla.Column(sqla.Integer)
    budget = sqla.Column(sqla.Integer)
    flex = sqla.Column(sqla.Boolean)
    theme = sqla.Column(sqla.String(255))
    date = sqla.Column(sqla.Date())
