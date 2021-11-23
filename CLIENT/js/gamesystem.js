import { Player } from './player.js'
import { Game } from './game.js'


export class GameSystem {
    constructor() {
        this.players = []
        this.game = new Game();
        this.eventsLog = [];
        this.adminMode = false;
    }

    createPlayers(numPlayers) {
        for (let i = 0; i < numPlayers; i++) {
            this.players.push(new Player());
        }
    }

    update(deltaTime) {
        this.game.update(deltaTime);
    }

    receiveEvent(message) {
        let payload = JSON.parse(message.data);

        console.log(payload);

        if (payload.type == "event") {
            if (payload.topic == "answer_visibility") {
                var elements = document.getElementsByClassName("answer-" + "abcd"[payload.data.answer_num]);
                var contents = elements[0].getElementsByClassName("answer-content");
                contents[0].style = payload.data.state == false ? "display: none;" : "";
            }

            if (payload.topic == "question_changed") {
                for (var i = 0; i < payload.data.answers.length; i++) {
                    var elements = document.getElementsByClassName("answer-" + "abcd"[i]);
                    var contents = elements[0].getElementsByClassName("answer-text");
                    //contents[0].style = "display: none;";
                    contents[0].textContent = payload.data.answers[i];
                }
            }
        }
        else if (payload.type == "game") {
            this.receiveGameUpdate(payload.content);
        }
        else if (payload.type == "player") {
            this.receivePlayerUpdate(payload.content, payload.playerId);
        }
        else if (payload.type == "game_event") {
            this.receiveGameUpdate(payload.game_data);

            if (payload.content == "end") {

            }
        }
        else if (payload.type == "timer_event") {
            this.receiveGameUpdate(payload.game_data);

            if (payload.content == "start") {
                this.game.start();
            }
            else if (payload.content == "pause") {
                this.game.pause();
            }
            else if (payload.content == "reset") {
                this.game.reset();
            }
            else if (payload.content == "set") {
                
            }
        }
    }

    receiveSystemUpdate(data) {
        this.players = []

        for (let p in data.players) {
            let newPlayer = new Player();
            newPlayer.receiveUpdate(data.players[p]);
            this.players.push(newPlayer);
        }

        this.game.receiveUpdate(data.game);
    }

    receiveGameUpdate(data) {
        this.game.receiveUpdate(data);
    }

    receivePlayerUpdate(data, playerNum) {
        this.players[playerNum].receiveUpdate(data);
    }
}
