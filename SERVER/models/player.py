from .serializable import Serializable


class Player(Serializable):
    def __init__(self):
        self.player_id = ""
        self.player_name = ""
        self.answer = None
        self.score = 0
        self.level = 0
