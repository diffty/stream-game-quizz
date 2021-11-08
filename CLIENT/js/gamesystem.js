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
        let data = JSON.parse(message.data);
        
        if (data.type == "game") {
            this.receiveGameUpdate(data.content);
        }
        else if (data.type == "player") {
            this.receivePlayerUpdate(data.content, data.playerId);
        }
        else if (data.type == "game_event") {
            this.receiveGameUpdate(data.game_data);

            if (data.content == "end") {

            }
        }
        else if (data.type == "timer_event") {
            this.receiveGameUpdate(data.game_data);

            if (data.content == "start") {
                this.game.start();
            }
            else if (data.content == "pause") {
                this.game.pause();
            }
            else if (data.content == "reset") {
                this.game.reset();
            }
            else if (data.content == "set") {
                
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
