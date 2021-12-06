from edh_league.sqla import sqla


class Commander(sqla.Model):
    id = sqla.Column(sqla.Integer(), primary_key=True, autoincrement=True)
    name = sqla.Column(sqla.String(255), unique=True)
    color_identity = sqla.Column(sqla.String(16))
    cmc = sqla.Column(sqla.Integer())
    type_line = sqla.Column(sqla.String(255))
    is_partner = sqla.Column(sqla.Boolean)
    link = sqla.Column(sqla.String(255))
    image_link = sqla.Column(sqla.String(255))
    scryfall_id = sqla.Column(sqla.String(64))
    mtg_set = sqla.Column(sqla.String(4))
    set_name = sqla.Column(sqla.String(64))
