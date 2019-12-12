from models import CommandersModel


class CommanderService:
    def __init__(self):
        self.model = CommandersModel()

    def create(self, params):
        self.model.create(params["name"], params["color"])

    def delete(self, commander_id):
        return self.model.delete(commander_id)

    def select(self):
        response = self.model.select()
        return response
