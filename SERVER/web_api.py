import json
from queue import Queue

from flask import Flask, jsonify, Response, request

from utils import print_to_console


NOTIFICATION_QUEUES = []

flask_app = Flask(__name__)

def event_stream(q):
    try:
        while True:
            message = q.get(True)
            print_to_console("Sending {}".format(message))
            yield "data: {}\n\n".format(message)
    finally:
        NOTIFICATION_QUEUES.remove(q)
        print_to_console("User quit")


@flask_app.route('/notifications_stream')
def notifications_stream():
    print_to_console("User Subscribed (count: %s)" % len(NOTIFICATION_QUEUES))

    q = Queue()
    NOTIFICATION_QUEUES.append(q)

    response = Response(event_stream(q), mimetype="text/event-stream")
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

from models.gamesystem import GameSystem
gameSystem = GameSystem()


@flask_app.route('/getGame')
def get_game():
    response = jsonify(gameSystem.game.to_json())
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@flask_app.route('/getSystem')
def get_system():
    #response = jsonify(gameSystem.to_json())
    response = jsonify(gameSystem.to_json())
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@flask_app.route('/getPlayer/<int:player_id>')
def get_player(player_id):
    response = jsonify(gameSystem.players[player_id].to_json())
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@flask_app.route('/getPlayerCount')
def get_player_count():
    response = jsonify(len(gameSystem.players))
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@flask_app.route('/updatePlayer/<int:player_id>', methods=['POST'])
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


@flask_app.route('/updateGame', methods=['POST'])
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


@flask_app.route('/setTimer', methods=['POST'])
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


@flask_app.route('/start', methods=['GET'])
def start():
    if request.method == "GET":
        gameSystem.game.start()
    
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@flask_app.route('/pause', methods=['GET'])
def pause():
    if request.method == "GET":
        gameSystem.game.pause()
    
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@flask_app.route('/reset', methods=['GET'])
def reset():
    if request.method == "GET":
        gameSystem.game.reset()
    
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response
