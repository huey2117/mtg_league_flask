from pgmodels import CommandersModel, UserDraftingModel, UsersModel, \
    ScoringModel, InfoModel, AdminModel


class CommanderService:
    def __init__(self):
        self.model = CommandersModel()

    def comm_page_view(self):
        response = self.model.comm_page_view()
        return response

    def team_page(self):
        response = self.model.team_page()
        return response


class DraftingService:
    def __init__(self):
        self.model = UserDraftingModel()

    def userid(self, username):
        user_id = self.model.get_user_id(username)
        return user_id

    def usercomm(self, user_id):
        response = self.model.check_usercomm(user_id)
        return response

    def draft(self, user_id):
        commander = self.model.draft_commander(user_id)
        if commander:
            return commander
        else:
            return "No Commanders Available"


class UserService:
    def __init__(self):
        self.model = UsersModel()


class ScoringService:
    def __init__(self):
        self.model = ScoringModel()

    def get_uid_username_pairs(self):
        response = self.model.get_uid_username_pairs()
        return response

    def add_scores(self, uid, game_id, pts_total, score):
        response = self.model.add_scores(uid, game_id, pts_total, score)
        return response

    def get_game_num_id(self):
        response = self.model.get_game_num_id()
        return response

    def get_standings(self):
        response = self.model.get_standings()
        return response

    def rebuild_standings(self):
        response = self.model.rebuild_standings()
        return response

    def restore_standings(self):
        response = self.model.restore_standings()
        return response

    def log_date(self, game_id, game_date):
        response = self.model.log_date(game_id, game_date)
        return response


class InfoService:
    def __init__(self):
        self.model = InfoModel()

    def get_curr_season_info(self):
        response = self.model.get_curr_season_info()
        return response

    def get_games_info(self):
        response = self.model.get_games_info()
        return response

    def get_curr_champ(self):
        response = self.model.get_curr_champ()
        return response


class AdminService:
    def __init__(self):
        self.model = AdminModel()

    def create_season(self, params):
        response = self.model.create_season(params)
        return response

    def add_games_to_season(self, params):
        response = self.model.add_games_to_season(params)
        return response

    def get_season_info(self):
        response = self.model.get_season_info()
        return response

    def start_season(self):
        response = self.model.start_season()
        return response

    def roll_challenges(self, params):
        response = self.model.roll_challenges(params)
        return response
