import os
import sys
import json
import datetime
import asyncio
import threading
import time
import traceback

from flask import Flask, jsonify, Response, request
import requests

from queue import Queue



NOTIFICATION_QUEUES = []



def print_to_console(s):
    print(s)
    sys.stdout.flush()


def to_json(var):
    res = None

    if hasattr(var, "to_json"):
        res = var.to_json()

    elif type(var) is dict:
        res = {}
        for k, v in var.items():
            res[k] = to_json(v)

    elif type(var) is list:
        res = []
        for v in var:
            res.append(to_json(v))

    else:
        res = var
    
    return res


class Serializable:
    def to_json(self):
        return to_json(self.__dict__)

    def from_json(self, data):
        for k, v in data.items():
            if k in self.__dict__:
                item = self.__dict__[k]
                if isinstance(item, Serializable):
                    item.from_json(v)
                    continue
                elif type(item) == bool:
                    self.__dict__[k] = v == "true"
                else:
                    self.__dict__[k] = type(item)(v)


class Player(Serializable):
    def __init__(self):
        self.playerName = ""
        self.oxygen = 75
        self.isDead = False
        self.role = ""


class Game(Serializable):
    def __init__(self):
        self.alarm = False
        self.currTime = 0
        self.maxTime = 3600
        self.maxOxygen = 75
        self.isTimerActive = False
        self.isGameEnded = True
        self.isGameStarted = False
    
    def start(self):
        self.isTimerActive = True
        self.on_timer_event("start")
    
    def pause(self):
        self.isTimerActive = False
        self.on_timer_event("pause")
    
    def reset(self):
        self.currTime = 0
        self.pause()
    
    def set_timer(self, new_time):
        gameSystem.game.currTime = new_time
        self.on_game_updated()
    
    def on_game_updated(self):
        event_payload = {
            "type": "game",
            "content": gameSystem.game.to_json(),
        }

        for q in NOTIFICATION_QUEUES:
            q.put(json.dumps(event_payload))
    
    def update(self, delta_time):
        if self.isTimerActive:
            self.currTime += delta_time
            if self.currTime >= self.maxTime and not self.isGameEnded:
                self.isGameEnded = True
                self.on_game_event("end")
    
    def on_timer_event(self, event_type):
        event_payload = {
            "type": "timer_event",
            "content": event_type,
            "game_data": gameSystem.game.to_json(),
        }

        for q in NOTIFICATION_QUEUES:
            q.put(json.dumps(event_payload))
    
    def on_game_event(self, event_type):
        event_payload = {
            "type": "game_event",
            "content": event_type,
            "game_data": gameSystem.game.to_json(),
        }

        for q in NOTIFICATION_QUEUES:
            q.put(json.dumps(event_payload))


class GameSystem(Serializable):
    def __init__(self):
        self.players = []
        self.game = None
    
        if os.path.exists("game_state.json"):
            self.load()
        else:
            self.create()

    def create(self):
        for i in range(4):
            self.players.append(Player())

        self.game = Game()
    
    def load(self):
        game_state = json.load(open("game_state.json", "r"))

        for p in game_state["players"]:
            new_player = Player()
            new_player.__dict__.update(p)

            self.players.append(new_player)
        
        self.game = Game()
        self.game.__dict__.update(game_state["game"])
    
    def save(self):
        json.load(self.to_json(), open("game_state.json", "w"))

    def update(self, delta_time):
        self.game.update(delta_time)

    #def to_json(self):
    #    return {
    #        "game": self.game.to_json(),
    #        "players": list(map(lambda p: p.to_json(), self.players.to_json())),
    #    }


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
