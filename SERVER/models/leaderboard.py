import json
from collections import OrderedDict

from models.serializable import Serializable

from utils import CustomJSONEncoder

from event_system import EventSystem



class Player(Serializable):
    def __init__(self, name: str):
        self.name = name
        self.score = 0
        self.level = 1
        self.answers_by_question = OrderedDict()
    
    def register_answer(self, question_id, answer_id):
        question_id_str = str(question_id)
        if question_id_str not in self.answers_by_question:
            self.answers_by_question[question_id_str] = answer_id
            print(f"<i> Registered player {self.name} answer {answer_id} for question {question_id_str}.")
        else:
            print(f"<!> Can't register player {self.name} answer {answer_id} for question {question_id_str} : question already answered.")


class Leaderboard(Serializable):
    def __init__(self, game_system):
        self.players = {}
        self._game_system = game_system
        self._score_by_level = [
            200,
            300,
            500,
            800,
            1500,
            3000,
            6000,
            12000,
            24000,
            48000,
            72000,
            100000,
            150000,
            300000,
            1000000,
            1250000,
            1800000,
            2000000,
            2500000,
            3000000,
            3500000,
            5000000,
        ]
        self._level_step_size = 4
    
    def create_player(self, player_name: str):
        return Player(player_name)
    
    def upgrade_player(self, player_name: str):
        self.players[player_name].level = self.calculate_upgrade(self.players[player_name].level)
        print(f"<i> Player {player_name} gain a level! They are now lvl {self.players[player_name].level}")
    
    def downgrade_player(self, player_name: str):
        player = self.players.get(player_name)

        if player and player.level > 1:
            old_level = self.players[player_name].level
            new_level = self.calculate_downgrade(self.players[player_name].level)
            self.players[player_name].level = new_level
            print(f"<i> Player {player_name} lose {new_level - old_level} level(s)! They are now lvl {self.players[player_name].level}")
    
    def calculate_upgrade(self, level: int):
        return level + 1

    def calculate_downgrade(self, level: int):
        if level > 1:
            return 1
        step_delta = level % self._level_step_size
        level -= step_delta
        if level < 1:
            level = 1
        return level

    def receive_answer(self, question_id: int, player_name: str, player_shuffled_answer: str):
        if not self.is_answer_valid(player_shuffled_answer):
            return
        
        answer_id = self._game_system.game._curr_question_obj.shuffled_answer_letter_to_id(player_shuffled_answer)

        print(f"REAL ANSWER ID: {answer_id}")
        print(f"ANSWERS MAP: {self._game_system.game._curr_question_obj._answers_order}")

        if player_name not in self.players:
            self.players[player_name] = self.create_player(player_name)
            print(f"<i> Player {player_name} registered!")

        self.players[player_name].register_answer(question_id, answer_id)
    
    def is_answer_valid(self, player_shuffled_answer: str):
        return player_shuffled_answer.upper() in "ABCD"
    
    def recalculate_scores(self, max_question_id):
        for p in self.players.values():
            p.score = 0
            p.level = 1

            for q_id in range(max_question_id+1):
                q_obj = self._game_system.game._q_db.get_question(q_id)
                p_score_gain, p_level_gain, reason = self.calculate_player_score_for_question(p.name,
                                                                                              q_id,
                                                                                              q_obj._correct_answer)
                p.score += p_score_gain
                p.level += p_level_gain

                good_shuffled_answer_id = q_obj.get_correct_answer_num()
                good_shuffled_answer_letter = "ABCD"[good_shuffled_answer_id]
                player_answer_id = p.answers_by_question.get(str(q_id), None)
                if player_answer_id is not None:
                    player_shuffled_answer_letter = "ABCD"[q_obj._answers_order[player_answer_id]]
                else:
                    player_shuffled_answer_letter = "-"

                print(" / ".join([
                    f"<i> Q{str(q_id).zfill(2)}: {p.name}",
                    f"{player_shuffled_answer_letter} ({good_shuffled_answer_letter})",
                    f"{player_answer_id if player_answer_id is not None else '-'} ({good_shuffled_answer_id})",
                    reason,
                    f"LVL {p_level_gain:+d}",
                    f"SCORE +{p_score_gain}",
                    f"TOTAL SCORE {p.score}",
                    f"TOTAL LVL {p.level}"
                ]))

        self.on_leaderboard_updated()
    
    def calculate_player_score_for_question(self, player_name: str, question_id: int, good_answer_id: int):
        if player_name not in self.players:
            raise Exception(f"<!!> Player {player_name} unknown.")
        
        p = self.players[player_name]
        old_level = new_level = p.level
        old_score = new_score = p.score
        reason = "UNKNOWN"

        player_answer_id = p.answers_by_question.get(str(question_id), None)
        if player_answer_id is not None:
            if player_answer_id == good_answer_id:
                new_level = self.calculate_upgrade(p.level)
                new_score = p.score + self._score_by_level[p.level-1]
                reason = "GOOD"
                
            else:
                new_level = self.calculate_downgrade(p.level)
                reason = "BAD"

        else:
            level_malus = 1 if p.level % self._level_step_size > 0 and p.level > 1 else 0
            new_level -= level_malus
            reason = "ABSENT"

        return new_score - old_score, new_level - old_level, reason

    def print_leaderboard(self):
        for p in self.players.values():
            print(f"{p.name}\t\t{p.level}\t{p.score}")

    def on_leaderboard_updated(self):
        event_payload = {
            "receiver": "leaderboard",
            "type": "data",
            "data": self.to_json(),
        }

        import web_api
        for q in web_api.NOTIFICATION_QUEUES:
            q.put(json.dumps(event_payload, cls=CustomJSONEncoder))
        
        EventSystem().emit("leaderboard_updated")

    def from_json(self, data):
        Serializable.from_json(self, data)
        for player_name, player_data in data["players"].items():
            new_player = Player(player_name)
            new_player.from_json(player_data)
            self.players[player_name] = new_player
