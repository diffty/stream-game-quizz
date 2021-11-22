import os
import json

from models.serializable import Serializable
from models.player import Player
from models.game import Game


class GameSystem(Serializable):
    def __init__(self):
        self.players = []
        self.game = None
    
        if os.path.exists("game_state.json"):
            self.load()
        else:
            self.create()

    def create(self):
        self.players = [Player()]
        self.game = Game()
    
    def load(self):
        game_state = json.load(open("game_state.json", "r"))

        for p in game_state["players"]:
            new_player = Player()
            new_player.__dict__.update(p)

            self.players.append(new_player)
        
        self.game = Game()
        self.game.__dict__.update(game_state["game"])
    
    def save(self):
        json.load(self.to_json(), open("game_state.json", "w"))

    def update(self, delta_time):
        self.game.update(delta_time)

    #def to_json(self):
    #    return {
    #        "game": self.game.to_json(),
    #        "players": list(map(lambda p: p.to_json(), self.players.to_json())),
    #    }
