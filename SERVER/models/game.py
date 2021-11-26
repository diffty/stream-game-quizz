import json

from gsheet_interface import auth
from question_db import QuestionDb

from .serializable import Serializable

from utils import CustomJSONEncoder


class Game(Serializable):
    def __init__(self):
        self._q_db = QuestionDb(auth(), "1ElFCYtnRjMb23gwZGZyBEBNREfsI_LhOEn_HXmpN4DY", 0)

        self.curr_question_id = 0
        self.curr_question_obj = None
        self.selected_answer_num = -1

        self.answers_visibility = []
        self.default_answer_visibility = False

        self.curr_question_time = 0
        self.max_question_time = 30
        self.is_timer_active = False
        self.is_game_ended = True
        self.is_game_started = False

        if self.curr_question_obj is None:
            self.set_question(0)
    
    def prev_question(self):
        if self.curr_question_id-1 < 0:
            raise Exception("<!!> Trying to access the question before the first one")

        self.set_question(self.curr_question_id-1)

    def next_question(self):
        if len(self._q_db.questions) <= self.curr_question_id+1:
            raise Exception("<!!> Trying to access the question after the first one")

        self.set_question(self.curr_question_id+1)
    
    def set_question(self, q_id: int):
        self.curr_question_id = q_id
        self.curr_question_obj = self._q_db.get_question(self.curr_question_id)
        self.selected_answer_num = -1
        self.answers_visibility = [self.default_answer_visibility] * len(self.curr_question_obj.answers)
        self.on_game_updated()
        print(f"{self.curr_question_obj.get_answers_list()=}")
        print(f"{q_id=}")

    def set_answer_visibility(self, answer_num: int, new_visibility: bool):
        self.answers_visibility[answer_num] = new_visibility
        self.on_game_updated()
        
    def set_answer_selection(self, answer_num: int):
        if (answer_num == -1 or self.answers_visibility[answer_num]):
            self.selected_answer_num = answer_num
            self.on_game_updated()
    
    def clear_answer_selection(self):
        self.selected_answer_num = -1
        self.on_game_event("answer_selection")

    def show_solution(self):
        self.emit_event("gamescreen", "show_solution", self.curr_question_obj.get_correct_answer_num())

    def hide_solution(self):
        self.emit_event("gamescreen", "hide_solution")
    
    def start_timer(self):
        self.is_timer_active = True
        self.on_timer_event("start")
    
    def pause_timer(self):
        self.is_timer_active = False
        self.on_timer_event("pause")
    
    def reset_timer(self):
        self.currTime = 0
        self.pause()
    
    def set_timer(self, new_time):
        self.curr_question_time = new_time
        self.on_game_updated()
    
    def update(self, delta_time):
        if self.is_timer_active:
            self.curr_question_time += delta_time
            if self.curr_question_time >= self.max_question_time and not self.is_game_ended:
                self.is_game_ended = True
                self.on_game_event("end")
    
    def on_question_changed(self):
        event_payload = {
            "receiver": "game",
            "type": "data",
            "data": {
                "curr_question_obj": self.curr_question_obj
            }
        }

        import web_api

        for q in web_api.NOTIFICATION_QUEUES:
            q.put(json.dumps(event_payload, cls=CustomJSONEncoder))
    
    def on_game_updated(self):
        event_payload = {
            "receiver": "game",
            "type": "data",
            "data": self.to_json(),
        }

        import web_api
        for q in web_api.NOTIFICATION_QUEUES:
            q.put(json.dumps(event_payload, cls=CustomJSONEncoder))

    def emit_event(self, receiver, topic, data=None):
        event_payload = {
            "receiver": receiver,
            "type": "event",
            "topic": topic,
            "data": data,
        }

        import web_api
        for q in web_api.NOTIFICATION_QUEUES:
            q.put(json.dumps(event_payload, cls=CustomJSONEncoder))

    def on_game_event(self, topic, data=None):
        self.emit_event("game", topic, data)
