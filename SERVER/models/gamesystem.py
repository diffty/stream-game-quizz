import os
import json

from models.serializable import Serializable
from models.game import Game
from utils import singleton

@singleton
class GameSystem(Serializable):
    def __init__(self):
        print("INIT GAMESYSTEM")
        self.game = None
    
        #f os.path.exists("game_state.json"):
        #   self.load()
        #lse:
        #   self.create()
        self.create()

    def create(self):
        self.game = Game(self)

    def load(self):
        game_state = json.load(open("game_state.json", "r"))

        print(f"{game_state=}")
        self.game = Game(self)
        self.game.from_json(game_state["game"])
    
    def save(self):
        json.dump(self.to_json(), open("game_state.json", "w"), indent=4)

    def update(self, delta_time):
        self.game.update(delta_time)

    #def to_json(self):
    #    return {
    #        "game": self.game.to_json(),
    #        "players": list(map(lambda p: p.to_json(), self.players.to_json())),
    #    }
