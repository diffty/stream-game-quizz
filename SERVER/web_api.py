import json
from queue import Queue

from flask import Flask, jsonify, Response, request

from utils import print_to_console


NOTIFICATION_QUEUES = []

GAME_SYSTEM = None

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


@flask_app.route('/getGame')
def get_game():
    response = jsonify(GAME_SYSTEM.game.to_json())
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@flask_app.route('/getLeaderboard')
def get_leaderboard():
    response = jsonify(GAME_SYSTEM.game.leaderboard.to_json())
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@flask_app.route('/getSystem')
def get_system():
    #response = jsonify(GAME_SYSTEM.to_json())
    response = jsonify(GAME_SYSTEM.to_json())
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@flask_app.route('/updateGame', methods=['POST'])
def update_game():
    if request.method == "POST":
        data = request.form

        print("caca:", data)
        
        GAME_SYSTEM.game.from_json(data)

        event_payload = {
            "type": "game",
            "content": GAME_SYSTEM.game.to_json(),
        }

        for q in NOTIFICATION_QUEUES:
            q.put(json.dumps(event_payload))
    
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response
