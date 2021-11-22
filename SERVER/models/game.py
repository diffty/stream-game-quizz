import json

from gsheet_interface import auth
from question_db import QuestionDb

from .serializable import Serializable


class Game(Serializable):
    def __init__(self):
        creds = auth()
        self.q_db = QuestionDb(creds, "1ElFCYtnRjMb23gwZGZyBEBNREfsI_LhOEn_HXmpN4DY", 0)
        self.curr_question_id = -1
        self.curr_question_obj = None
        self.selected_answer_number = -1

        self.curr_question_time = 0
        self.max_question_time = 30
        self.is_timer_active = False
        self.is_game_ended = True
        self.is_game_started = False
    
    def next_question(self):
        if len(self.q_db.question) <= self.curr_question_id+1:
            raise Exception("<!!> Trying to access the question after the first one")

        self.set_question(self.curr_question_id+1)
    
    def prev_question(self):
        if self.curr_question_id-1 < 0:
            raise Exception("<!!> Trying to access the question before the first one")

        self.set_question(self.curr_question_id-1)

    def set_question(self, q_id: int):
        self.curr_question_obj = self.q_db.get_question(self.curr_question_id)
        self.curr_question_id = q_id
        self.on_game_event("question_change")

    def set_answer_selection(self, a_number: int):
        self.selected_answer_number = a_number
        self.on_game_event("answer_selection")
    
    def clear_answer_selection(self):
        self.selected_answer_number = -1
        self.on_game_event("answer_selection")

    def show_solution(self):
        self.on_game_event("show_solution")

    def hide_solution(self):
        self.on_game_event("hide_solution")
    
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
    
    def on_game_updated(self):
        event_payload = {
            "type": "game",
            "content": self.to_json(),
        }

        for q in NOTIFICATION_QUEUES:
            q.put(json.dumps(event_payload))
    
    def on_timer_event(self, event_type):
        event_payload = {
            "type": "timer_event",
            "content": event_type,
            "game_data": self.to_json(),
        }

        for q in NOTIFICATION_QUEUES:
            q.put(json.dumps(event_payload))
    
    def on_game_event(self, event_type):
        event_payload = {
            "type": "game_event",
            "content": event_type,
            "game_data": self.to_json(),
        }

        for q in NOTIFICATION_QUEUES:
            q.put(json.dumps(event_payload))
