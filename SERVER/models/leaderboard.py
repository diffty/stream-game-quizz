import json
from collections import OrderedDict

from models.serializable import Serializable

from utils import CustomJSONEncoder


class Player(Serializable):
    def __init__(self, name: str):
        self.name = name
        self.score = 0
        self.level = 1
        self.answers_by_question = OrderedDict()
    
    def register_answer(self, question_id, answer):
        if question_id not in self.answers_by_question:
            self.answers_by_question[question_id] = answer
            print(f"<i> Registered player {self.name} answer {answer} for question {question_id}.")
        else:
            print(f"<!> Can't register player {self.name} answer {answer} for question {question_id} : question already answered.")


class Leaderboard(Serializable):
    _instance = None

    def __init__(self):
        self.players = {}
        self.score_by_level = [200, 300, 500, 800, 1500, 3000, 6000, 12000, 24000, 48000, 72000, 100000, 150000, 300000, 1000000]
        self.level_step_size = 4

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def create_player(self, player_name: str):
        return Player(player_name)
    
    def upgrade_player(self, player_name: str):
        self.players[player_name].level += 1
        print(f"<i> Player {player_name} gain a level! They are now lvl {self.players[player_name].level}")
    
    def downgrade_player(self, player_name: str):
        player = self.players.get(player_name)

        if player and player.level > 1:
            step_delta = self.players[player_name].level % self.level_step_size
            self.players[player_name].level -= step_delta
            if self.players[player_name].level < 1:
                self.players[player_name].level = 1
            print(f"<i> Player {player_name} lose {step_delta} level(s)! They are now lvl {self.players[player_name].level}")
    
    def receive_answer(self, question_id: int, player_name: str, answer: str):
        if not self.is_answer_valid(answer):
            return

        if player_name not in self.players:
            self.players[player_name] = self.create_player(player_name)
            print(f"<i> Player {player_name} registered!")

        self.players[player_name].register_answer(question_id, answer)
    
    def is_answer_valid(self, answer: str):
        return answer.upper() in "ABCD"
    
    def calculate_scores(self, question_id: int, question_answer: str):
        for p in self.players.values():
            answer = p.answers_by_question.get(question_id, None)
            if answer is not None:
                if answer.upper() == question_answer.upper():
                    self.upgrade_player(p.name)
                    score_gain = self.score_by_level[p.level-1]
                    p.score += score_gain
                    print(f"<i> Q{str(question_id).zfill(2)}: {p.name} / LVL +1 / SCORE +{score_gain} / TOTAL SCORE {p.score} / TOTAL LVL {p.level}")
                else:
                    self.downgrade_player(p.name)
                    print(f"<i> Q{str(question_id).zfill(2)}: {p.name} / LVL -- / SCORE +0 / TOTAL SCORE {p.score} / TOTAL LVL {p.level}")
            else:
                level_malus = 1 if p.level % self.level_step_size > 0 and p.level > 1 else 0
                p.level -= level_malus
                print(f"<i> Player {p.name} did not respond; losing {level_malus} level. They are now lvl {p.level}")
                print(f"<i> Q{str(question_id).zfill(2)}: {p.name} / LVL -- / SCORE +0 / TOTAL SCORE {p.score} / TOTAL LVL {p.level}")

    def print_leaderboard(self):
        for p in self.players.values():
            print(f"{p.name}\t\t{p.level}\t{p.score}")
