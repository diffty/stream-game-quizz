import sys
import json
import threading
import time

from flask import Flask, jsonify, Response, request

from queue import Queue

from utils import print_to_console
from models.gamesystem import GameSystem


NOTIFICATION_QUEUES = []


app = Flask(__name__)
gameSystem = GameSystem()


def main():
    then = time.time()

    while True:
        now = time.time()
        deltaTime = now - then
        then = now

        gameSystem.update(deltaTime)

        sys.stdout.flush()
        sys.stderr.flush()

t = threading.Thread(target=main)
t.start()


def event_stream(q):
    try:
        while True:
            message = q.get(True)
            print_to_console("Sending {}".format(message))
            yield "data: {}\n\n".format(message)
    finally:
        NOTIFICATION_QUEUES.remove(q)
        print_to_console("User quit")


@app.route('/notifications_stream')
def notifications_stream():
    print_to_console("User Subscribed (count: %s)" % len(NOTIFICATION_QUEUES))

    q = Queue()
    NOTIFICATION_QUEUES.append(q)

    response = Response(event_stream(q), mimetype="text/event-stream")
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@app.route('/getGame')
def get_game():
    response = jsonify(gameSystem.game.to_json())
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@app.route('/getSystem')
def get_system():
    response = jsonify(gameSystem.to_json())
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@app.route('/getPlayer/<int:player_id>')
def get_player(player_id):
    response = jsonify(gameSystem.players[player_id].to_json())
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@app.route('/getPlayerCount')
def get_player_count():
    response = jsonify(len(gameSystem.players))
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@app.route('/updatePlayer/<int:player_id>', methods=['POST'])
def update_player(player_id):
    if request.method == "POST":
        data = request.form

        print("caca:", data)
        
        gameSystem.players[player_id].from_json(data)

        event_payload = {
            "type": "player",
            "playerId": player_id,
            "content": gameSystem.players[player_id].to_json(),
        }

        for q in NOTIFICATION_QUEUES:
            q.put(json.dumps(event_payload))
    
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@app.route('/updateGame', methods=['POST'])
def update_game():
    if request.method == "POST":
        data = request.form

        print("caca:", data)
        
        gameSystem.game.from_json(data)

        event_payload = {
            "type": "game",
            "content": gameSystem.game.to_json(),
        }

        for q in NOTIFICATION_QUEUES:
            q.put(json.dumps(event_payload))
    
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@app.route('/setTimer', methods=['POST'])
def set_timer(new_time):
    if request.method == "POST":
        data = request.get_json()
        if "newTime" in data:
            gameSystem.game.currTime = data["newTime"]

            event_payload = {
                "type": "game",
                "content": jsonify(gameSystem.game.to_json()),
            }

            for q in NOTIFICATION_QUEUES:
                q.put(json.dumps(event_payload))

    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')
    
    return ""


@app.route('/start', methods=['GET'])
def start():
    if request.method == "GET":
        gameSystem.game.start()
    
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@app.route('/pause', methods=['GET'])
def pause():
    if request.method == "GET":
        gameSystem.game.pause()
    
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@app.route('/reset', methods=['GET'])
def reset():
    if request.method == "GET":
        gameSystem.game.reset()
    
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtWidgets import QWidget, QPushButton
from PySide2.QtCore import QThread

from twitchio.ext import commands


class FlaskApplicationThead(QThread):
    def __init__(self, app: Flask, port: int = 5000):
        QThread.__init__(self)
        self.app = app
        self.port = port
    
    def run(self):
        self.app.run(port=self.port, threaded=True)



class Bot(commands.Bot):
    def __init__(self):
        super().__init__(token='f2zdd226wyugv6luydhkjcvc47wmd5', prefix='!', initial_channels=['diffty'])  # coxwfoge6t8mnd8f1xednqvo6c20un
        
    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')

    @commands.command()
    async def hello(self, ctx: commands.Context):
        # Send a hello back!
        await ctx.send(f'Hello {ctx.author.name}!')
    

bot = Bot()


class BotApplicationThead(QThread):
    def __init__(self, bot: commands.Bot):
        QThread.__init__(self)
        self.bot = bot
    
    def run(self):
        self.bot.run()


qt_app = QApplication()

#b_app = BotApplicationThead(bot)
#b_app.start()

bot.run()

f_app = FlaskApplicationThead(app)
f_app.start()

w = QPushButton()
w.show()

qt_app.exec_()
