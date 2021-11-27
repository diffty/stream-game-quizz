from typing import List

from models.gamesystem import GameSystem

from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout
from PySide6.QtWidgets import QWidget, QPushButton, QLineEdit, QCheckBox
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem

from PySide6.QtCore import Signal

from models.leaderboard import Player


class PlayerListItem(QTreeWidgetItem):
    def __init__(self, player_obj):
        QTreeWidgetItem.__init__(self, [player_obj.name, str(player_obj.level), str(player_obj.score)])
        self.player_obj = player_obj


class PlayerList(QTreeWidget):
    def __init__(self):
        QTreeWidget.__init__(self)
        self.setColumnCount(3)
        self.setHeaderLabels(["Name", "Level", "Score"])
    
    def update(self, players: List[Player]):
        self.clear()
        for player_obj in players.values():
            self.addTopLevelItem(PlayerListItem(player_obj))


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
    question_changed = Signal(int)
    answer_visibility_changed = Signal(int, bool)
    answer_selected = Signal(int)
    answer_cleared = Signal()
    reveal_answer = Signal()

    def __init__(self, game_system: GameSystem):
        QMainWindow.__init__(self)

        self.setWindowTitle("Qui Veut Manier des Galions - Control Panel")
        self.resize(1000, 700)

        self.game_system = game_system
        
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
        reveal_answer_btn.clicked.connect(self.reveal_answer)
        main_layout.addWidget(reveal_answer_btn)

        clear_answer_btn = QPushButton(text="Clear Answer")
        clear_answer_btn.clicked.connect(self.on_clear_answer)
        main_layout.addWidget(clear_answer_btn)

        switch_question_layout = QHBoxLayout()

        prev_question_btn = QPushButton(text="<--")
        next_question_btn = QPushButton(text="-->")
        prev_question_btn.clicked.connect(self.on_prev_question)
        next_question_btn.clicked.connect(self.on_next_question)
        switch_question_layout.addWidget(prev_question_btn)
        switch_question_layout.addWidget(next_question_btn)

        main_layout.addLayout(switch_question_layout)

        self.player_list_widget = PlayerList()
        main_layout.addWidget(self.player_list_widget)

        recalculate_score_btn = QPushButton(text="Recalculate Scores")
        recalculate_score_btn.clicked.connect(self.on_recalculate_scores)
        main_layout.addWidget(recalculate_score_btn)

        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)

        self.refresh_ui()
    
    def on_prev_question(self):
        self.game_system.game.prev_question()
        self.refresh_ui()
        self.question_changed.emit(self.game_system.game.curr_question_id)

    def on_next_question(self):
        self.game_system.game.next_question()
        self.refresh_ui()
        self.question_changed.emit(self.game_system.game.curr_question_id)
    
    def on_clear_answer(self):
        self.answer_selected.emit(-1)
    
    def on_recalculate_scores(self):
        self.game_system.game.leaderboard.recalculate_scores(self.game_system.game.curr_question_id)

    def leaderboard_update(self):
        self.player_list_widget.update(self.game_system.game.leaderboard.players)

    def refresh_ui(self):
        self.question_field.setText(self.game_system.game._curr_question_obj.question)

        answers_list = self.game_system.game._curr_question_obj.get_answers_list()
        for i, a_widget in enumerate(self.answer_widget_list):
            a_widget.set_answer_text(answers_list[i] if i < len(answers_list) else "")
            a_widget.answer_checkbox.setChecked(self.game_system.game.answers_visibility[i])

        self.leaderboard_update()