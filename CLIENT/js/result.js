import { CONFIG } from '../config.js'

import { GameSystem } from './gamesystem.js'
import { EventSystem } from './eventsystem.js';


export class Leaderboard {
    constructor(game) {
        this.game = game;
        this.result_content = document.getElementsByClassName("result-content");

        EventSystem.connect("leaderboard_message_received", (payload) => { this.receiveMessage(payload) });
        EventSystem.connect("leaderboard_updated", () => { this.onLeaderboardUpdate() });
    }
    
    receiveMessage(payload) {
        if (payload.receiver == "leaderboard") {
            if (payload.type == "event") {
                this.receiveEvent(payload);
            }
            else if (payload.type == "data") {
                this.receiveUpdate(payload.data);
            }
        }
    }

    retrieveUpdate() {
        $.ajax({
            url: `http://${CONFIG.host}:${CONFIG.port}/getLeaderboard`
        }).then((data) => {
            this.receiveUpdate(data)
        });
    }

    receiveEvent(payload) {
        
    }
    
    receiveUpdate(data) {
        console.log(data);
        this.result_content[0].textContent = data.players["danny"].score + " D"
    }

    cleanTable() {
        var nbRows = this.leaderboardTable.rows.length;
        for (var i = 0; i < nbRows-1; i++) {
            this.leaderboardTable.deleteRow(1);
        }
    }

    updateTable(data) {
        for (var key in data.players) {
            var p = data.players[key];

            var nouvelleLigne = this.leaderboardTable.insertRow(this.leaderboardTable.rows.length);

            var playerNameCell = nouvelleLigne.insertCell(0);
            playerNameCell.textContent = p.name;

            var levelCell = nouvelleLigne.insertCell(1);
            levelCell.textContent = p.level;
            levelCell.className = "level"

            var scoreCell = nouvelleLigne.insertCell(2);
            scoreCell.textContent = p.score;
            scoreCell.className = "score"
        }
    }

    update(deltaTime) {
        
    }
}


var gameSystem = new GameSystem();
var leaderboard = new Leaderboard(gameSystem.game);
leaderboard.retrieveUpdate()

let eventSource = new EventSource(`http://${CONFIG.host}:${CONFIG.port}/notifications_stream`);

eventSource.onmessage = (message) => {
    let payload = JSON.parse(message.data);
    console.log(payload);
    EventSystem.emit(`${payload.receiver}_message_received`, payload)
};
