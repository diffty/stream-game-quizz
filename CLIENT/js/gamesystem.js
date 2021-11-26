import { CONFIG } from '../config.js'

import { Player } from './player.js'
import { Game } from './game.js'
import { EventSystem } from './eventsystem.js'


export class GameSystem {
    constructor() {
        this.players = []
        this.game = new Game();
        this.eventsLog = [];
        this.adminMode = false;
        
        EventSystem.connect("gamesystem_message_received", (payload) => { this.receiveMessage(payload) });

        this.retrieveUpdate();
    }

    createPlayers(numPlayers) {
        for (let i = 0; i < numPlayers; i++) {
            this.players.push(new Player());
        }
    }

    update(deltaTime) {
        this.game.update(deltaTime);
    }

    retrieveUpdate() {
        $.ajax({
            url: `http://${CONFIG.host}:${CONFIG.port}/getSystem`
        }).then((data) => {
            this.receiveUpdate(data)
        });
    }

    receiveMessage(payload) {
        if (payload.receiver == "gamesystem") {
            if (payload.type == "event") {
                this.receiveEvent(payload)
            }
            else if (payload.type == "data") {
                this.receiveUpdate(payload.data);
            }
        }
    }

    receiveEvent(payload) {

    }

    receiveUpdate(data) {
        this.players = []

        for (let p in data.players) {
            let newPlayer = new Player();
            newPlayer.receiveUpdate(data.players[p]);
            this.players.push(newPlayer);
        }

        this.game.receiveUpdate(data.game);
    }

    receivePlayerUpdate(data, playerNum) {
        this.players[playerNum].receiveUpdate(data);
    }
}
