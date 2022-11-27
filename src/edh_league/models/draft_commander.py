from src.edh_league.sqla import sqla


class DraftCommander(sqla.Model):
    id = sqla.Column(sqla.Integer, primary_key=True, autoincrement=True)
    commander_id = sqla.Column(sqla.Integer, sqla.ForeignKey('admin.commanders.id'))
    draft_rank = sqla.Column(sqla.Integer)