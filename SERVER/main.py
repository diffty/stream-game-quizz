import sys
import threading
import asyncio
import time
import json

import web_api
from models.gamesystem import GameSystem
from models.leaderboard import Leaderboard
from ui import ControllerGUI
from event_system import EventSystem

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThread

from flask import Flask

from twitchio.ext import commands


# Define web API QThread
class FlaskApplicationThread(QThread):
    def __init__(self, app: Flask, port: int = 5000):
        QThread.__init__(self)
        self.app = app
        self.port = port
    
    def run(self):
        self.app.run(host="0.0.0.0", port=self.port, threaded=True)


# Define bot QThread
class BotApplicationThread(QThread):
    def __init__(self, bot: commands.Bot):
        QThread.__init__(self)
        self.bot = bot
    
    def run(self):
        self.bot.run()


# Define bot
class Bot(commands.Bot):
    def __init__(self, game_system: GameSystem):
        super().__init__(token='f2zdd226wyugv6luydhkjcvc47wmd5',
                         prefix='!',
                         initial_channels=['diffty'])

        self.game_system = game_system
        
    async def event_ready(self):
        print(f'Logged in as | {self.nick}')

    @commands.command()
    async def zamak(self, ctx: commands.Context):
        await ctx.send(f'Zamak à toi, {ctx.author.name}')

    @commands.command()
    async def la(self, ctx: commands.Context):
        self.receive_answer(ctx.author.name, ctx.message.content)
        
    @commands.command()
    async def reponse(self, ctx: commands.Context):
        self.receive_answer(ctx.author.name, ctx.message.content)
        
    @commands.command()
    async def lareponse(self, ctx: commands.Context):
        self.receive_answer(ctx.author.name, ctx.message.content)

    def receive_answer(self, user_name, message_content):
        answer = self.search_for_answers(message_content)

        if answer:
            self.game_system.game.leaderboard.receive_answer(self.game_system.game.curr_question_id,
                                                             user_name,
                                                             answer)

            EventSystem().emit("leaderboard_updated")

    @staticmethod
    def search_for_answers(message_content):
        splitted_content = message_content.split(" ")[1:]
        results = list(filter(lambda word: word.upper() in "ABCD", splitted_content))
        if results:
            return results[0]
        else:
            return None

    async def say_question(self):
        question = self.game_system.game._curr_question_obj.question
        await bot.get_channel("diffty").send(f"Question : {question}")
        
    async def say_answer(self, answer_num: int):
        answers = self.game_system.game._curr_question_obj.get_answers_list()
        await bot.get_channel("diffty").send(f"Réponse {'ABCD'[answer_num]} : {answers[answer_num]}")


if __name__ == "__main__":
    # Init Game System
    game_system = GameSystem()

    # Init Twitch Bot
    bot = Bot(game_system)
    bot_thread = BotApplicationThread(bot)
    bot_thread.start()

    # Init Web API
    web_api.GAME_SYSTEM = game_system
    flask_thread = FlaskApplicationThread(web_api.flask_app)
    flask_thread.start()

    # Init UI
    qt_app = QApplication()

    main_window = ControllerGUI(game_system)
    main_window.show()

    ui_loop = asyncio.new_event_loop()

    def _say_answer_on_reveal(answer_num: int, answer_state: bool):
        ui_loop.run_until_complete(bot.say_answer(answer_num))

    def _say_question_on_reveal(question_num: int):
        ui_loop.run_until_complete(bot.say_question())

    def _save_state():
        game_system.save()

    main_window.question_changed.connect(_say_question_on_reveal)
    main_window.question_changed.connect(_save_state)
    main_window.answer_visibility_changed.connect(_say_answer_on_reveal)
    main_window.answer_visibility_changed.connect(game_system.game.set_answer_visibility)
    main_window.answer_selected.connect(game_system.game.set_answer_selection)
    main_window.reveal_answer.connect(game_system.game.show_solution)

    EventSystem().connect("leaderboard_updated", main_window.leaderboard_update)

    qt_app.aboutToQuit.connect(flask_thread.terminate)
    qt_app.aboutToQuit.connect(bot_thread.terminate)

    qt_app.exec()
