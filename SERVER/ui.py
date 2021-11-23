from models.gamesystem import GameSystem

from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout
from PySide6.QtWidgets import QWidget, QPushButton, QLineEdit, QCheckBox

from PySide6.QtCore import Signal


class AnswerWidget(QWidget):
    visibility_changed = Signal(int, bool)
    answer_selected = Signal(int)

    def __init__(self, num: int, name: str):
        QWidget.__init__(self)

        self.num = num
        self.name = name

        answer_layout = QHBoxLayout()
        self.setLayout(answer_layout)

        self.answer_checkbox = QCheckBox()
        self.answer_btn = QPushButton(text=name)
        self.answer_text = QLineEdit(text="")

        self.answer_checkbox.stateChanged.connect(self.on_answer_visibility_change)
        self.answer_btn.clicked.connect(self.on_answer_selected)

        answer_layout.addWidget(self.answer_checkbox)
        answer_layout.addWidget(self.answer_btn)
        answer_layout.addWidget(self.answer_text)
    
    def set_answer_text(self, new_text):
        self.answer_text.setText(new_text)
    
    def on_answer_visibility_change(self, new_state):
        self.visibility_changed.emit(self.num, new_state)

    def on_answer_selected(self):
        self.answer_selected.emit(self.num)


class ControllerGUI(QMainWindow):
    answer_visibility_changed = Signal(int, bool)
    answer_selected = Signal(int)

    def __init__(self):
        QMainWindow.__init__(self)

        self.game_system = GameSystem()
        
        main_widget = QWidget()

        main_layout = QVBoxLayout()

        self.question_field = QLineEdit()
        main_layout.addWidget(self.question_field)

        answers_layout = QVBoxLayout()

        self.answer_widget_list = []

        for i, letter in enumerate(["A", "B", "C", "D"]):
            answer_widget = AnswerWidget(i, letter)
            answers_layout.addWidget(answer_widget)
            self.answer_widget_list.append(answer_widget)
            answer_widget.visibility_changed.connect(self.answer_visibility_changed)
            answer_widget.answer_selected.connect(self.answer_selected)

        main_layout.addLayout(answers_layout)

        reveal_answer_btn = QPushButton(text="Reveal Answer")
        main_layout.addWidget(reveal_answer_btn)

        switch_question_layout = QHBoxLayout()
        prev_question_btn = QPushButton(text="<--")
        next_question_btn = QPushButton(text="-->")
        switch_question_layout.addWidget(prev_question_btn)
        switch_question_layout.addWidget(next_question_btn)
        main_layout.addLayout(switch_question_layout)

        prev_question_btn.clicked.connect(self.on_prev_question)
        next_question_btn.clicked.connect(self.on_next_question)

        main_layout.addStretch()

        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)
    
    def on_prev_question(self):
        self.game_system.game.prev_question()
        self.refresh_ui()

    def on_next_question(self):
        self.game_system.game.next_question()
        self.refresh_ui()
    
    def refresh_ui(self):
        self.question_field.setText(self.game_system.game.curr_question_obj.question)

        answers_list = self.game_system.game.curr_question_obj.get_answers_list()
        for i, a_widget in enumerate(self.answer_widget_list):
            a_widget.set_answer_text(answers_list[i] if i < len(answers_list) else "")
