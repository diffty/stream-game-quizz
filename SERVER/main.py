import sys
import threading
import asyncio
import time
import json

import web_api
from models.gamesystem import GameSystem
from ui import ControllerGUI

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThread

from flask import Flask

from twitchio.ext import commands


# Flask
class FlaskApplicationThread(QThread):
    def __init__(self, app: Flask, port: int = 5000):
        QThread.__init__(self)
        self.app = app
        self.port = port
    
    def run(self):
        self.app.run(port=self.port, threaded=True)


# Bot
class BotApplicationThread(QThread):
    def __init__(self, bot: commands.Bot):
        QThread.__init__(self)
        self.bot = bot
    
    def run(self):
        self.bot.run()


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(token='f2zdd226wyugv6luydhkjcvc47wmd5', prefix='!', initial_channels=['diffty'])  # coxwfoge6t8mnd8f1xednqvo6c20un
        
    async def event_ready(self):
        print(f'Logged in as | {self.nick}')

    @commands.command()
    async def hello(self, ctx: commands.Context):
        await ctx.send(f'Hello {ctx.author.name}!')


if __name__ == "__main__":
    # Game System
    game_system = GameSystem()

    # Init Twitch Bot
    bot = Bot()
    bot_thread = BotApplicationThread(bot)
    bot_thread.start()

    # Init Web API
    flask_thread = FlaskApplicationThread(web_api.flask_app)
    flask_thread.start()

    # UI
    qt_app = QApplication()
    ui_loop = asyncio.new_event_loop()

    main_window = ControllerGUI()
    main_window.show()

    def _answer_visibility_changed(answer_num, new_state):
        answers = game_system.game.curr_question_obj.get_answers_list()

        async def _say_answer():
            await bot.get_channel("diffty").send(f"Réponse {'ABCD'[answer_num]} : {answers[answer_num]}")

        ui_loop.run_until_complete(_say_answer())

        event_payload = {
            "type": "event",
            "topic": "answer_visibility",
            "data": {
                "answer_num": answer_num,
                "state": new_state
            }
        }

        for q in web_api.NOTIFICATION_QUEUES:
            q.put(json.dumps(event_payload))

    main_window.answer_visibility_changed.connect(_answer_visibility_changed)

    # Start Game Loop
    def game_system_loop():
        then = time.time()

        while True:
            now = time.time()
            deltaTime = now - then
            then = now

            # Code here
            
            time.sleep(0.0166)

            sys.stdout.flush()
            sys.stderr.flush()


    t = threading.Thread(target=game_system_loop)
    t.start()

    qt_app.exec()
