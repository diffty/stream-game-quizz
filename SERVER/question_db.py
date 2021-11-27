import sys
import random

from gsheet_interface import get_info, auth

from models.serializable import Serializable


class Question(Serializable):
    def __init__(self, question, answers, correct_answer=0) -> None:
        self.question = question
        self.answers = answers

        self._correct_answer = correct_answer
        self._answers_order = list(range(len(answers)))

        self.shuffle_answers()

    def shuffle_answers(self):
        random.shuffle(self._answers_order)
    
    def get_answers_list(self):
        return list(map(lambda i: self.answers[i], self._answers_order))
    
    def get_correct_answer_num(self):
        return self._answers_order[self._correct_answer]
    
    def shuffled_answer_letter_to_id(self, answer_letter: str):
        return self._answers_order[ord(answer_letter.upper())-65]

    def __repr__(self):
        return f"<Question: {self.question} - {' / '.join(self.answers)}>"
    
    def to_json(self):
        return {"question": self.question, "answers": self.get_answers_list()}

    @staticmethod
    def create_from_row(row_content):
        answers = list(filter(lambda c: c != '' and c != None, row_content[1:]))
        return Question(row_content[0], answers)


class QuestionDb:
    def __init__(self, creds, spreadsheet_id, sheet_id):
        self.creds = creds
        self.spreadsheet_id = spreadsheet_id
        self.sheet_id = sheet_id
        
        self.questions = []

        self.refresh()
    
    def refresh(self):
        gsheet_content = list(filter(lambda row: len(row) >= 2,
                                     get_info(self.creds, self.spreadsheet_id, self.sheet_id, "A2:E300")))
        self.questions = list(map(lambda r: Question.create_from_row(r), gsheet_content))
    
    def get_question(self, id) -> Question:
        if id < 0 or id >= len(self.questions):
            raise Exception(f"<!!> Question id {id} is invalid (out of range)")

        return self.questions[id]


if __name__ == "__main__":
    import os

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    if len(sys.argv) >= 3:
        spreadsheet_id = sys.argv[1]
        sheet_id = sys.argv[2]
    else:
        spreadsheet_id = "1ElFCYtnRjMb23gwZGZyBEBNREfsI_LhOEn_HXmpN4DY"
        sheet_id = 0


    creds = auth()
    qdb = QuestionDb(creds, spreadsheet_id, sheet_id)
