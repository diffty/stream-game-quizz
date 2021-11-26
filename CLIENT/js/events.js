import { CONFIG } from '../config.js'

import { GameSystem } from './gamesystem.js'


var gameSystem = new GameSystem();


function updateSystem(gameSystem) {
    $.ajax({
        url: `http://${CONFIG.host}:${CONFIG.port}/getSystem`
    }).then((data) => {
        gameSystem.receiveSystemUpdate(data)
    });
}


var eventList = []


function getFormattedTime(timestamp) {
    let hours = Math.floor(timestamp / 3600) % 24;
    let minutes = Math.floor(timestamp / 60) % 60;
    let seconds = Math.floor(timestamp) % 60;
    return `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`
}

function updateOutput() {
    $("#output").empty();

    console.log(eventList);
    for (let i = eventList.length-1 ; i >= 0; i--) {
        let newEvent = document.createElement("span");
        newEvent.innerHTML = eventList[i];
        $("#output").append(newEvent);
    }
}


function outputString(s) {
    eventList.push(`[${getFormattedTime(gameSystem.game.currTime)}] ${s}<br />`);
    updateOutput();
}


updateSystem(gameSystem);


let eventSource = new EventSource(`http://${CONFIG.host}:${CONFIG.port}/notifications_stream`);
eventSource.onmessage = (message) => {
    let data = JSON.parse(message.data);

    if (data.type == "player") {
        let playerNum = data.playerId;
        let localPlayer = gameSystem.players[playerNum];

        for (var i in data.content) {
            if (localPlayer[i] != data.content[i]) {
                switch (i) {
                    case "isDead":
                        if (data.content[i] == true) {
                            outputString(`${data.content.playerName} est mort :(`)
                        }
                        else {
                            outputString(`${data.content.playerName} n'est plus mort !`)
                        }
                    break;

                    case "oxygen":
                        let oxygenDelta = data.content.oxygen - localPlayer.oxygen;
                        if (oxygenDelta > 0) {
                            outputString(`${data.content.playerName} gagne +${oxygenDelta} points d'oxygène !`)
                        }
                        else {
                            outputString(`${data.content.playerName} perd ${oxygenDelta} points d'oxygène !`)
                        }
                    break;
                }
            }
        }
    }
    else if (data.type == "game") {
        let localGame = gameSystem.game;

        for (var i in data.content) {
            if (localGame[i] != data.content[i]) {
                switch (i) {
                    case "alarm":
                        if (data.content[i] == true) {
                            outputString(`Catastrophe en cours !`)
                        }
                        else {
                            outputString(`Fin de la catastrophe.`)
                        }
                    break;
                }
            }
        }
    }

    gameSystem.receiveEvent(message);
};


// VARS
let then = 0;

function animate(now) {
    now *= 0.001;
    
    const deltaTime = now - then;
    then = now;

    gameSystem.update(deltaTime);

    requestAnimationFrame(animate);
}

requestAnimationFrame(animate);
