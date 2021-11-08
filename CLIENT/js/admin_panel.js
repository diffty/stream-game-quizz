import { GameSystem } from './gamesystem.js'
import { CONFIG } from '../config.js'


export var gameSystem = new GameSystem();
gameSystem.adminMode = true;

let playerElementList = []

$("#game").bind("changed", (e) => {
    let newData = {}

    newData[e.detail.propertyName] = e.detail.newValue;
    
    $.post({
        url: `http://${CONFIG.host}:${CONFIG.port}/updateGame`,
        data: newData,
        dataType: "json",
    });
})

function updateSystem() {
    $.ajax({
        url: `http://${CONFIG.host}:${CONFIG.port}/getSystem`
    }).then((data) => {
        gameSystem.receiveSystemUpdate(data)

        $("#players").empty();

        playerElementList = []

        for (let k in data.game) {
            let v = data.game[k];
            $("#game").prop(k, v);
        }

        for (let i in data.players) {
            let p = data.players[i];

            let newPlayerElement = document.createElement("player-element");

            newPlayerElement["playerNum"] = new Number(i);
            newPlayerElement["playerName"] = p.playerName;
            newPlayerElement["role"] = p.role;
            newPlayerElement["oxygen"] = p.oxygen;
            newPlayerElement["isDead"] = p.isDead;
            newPlayerElement["adminMode"] = true;
            newPlayerElement["maxOxygen"] = gameSystem.game.maxOxygen;

            playerElementList.push(newPlayerElement);

            newPlayerElement.addEventListener("changed", (e) => {
                let newData = {}

                newData[e.detail.propertyName] = e.detail.newValue;
                
                $.post({
                    url: `http://${CONFIG.host}:${CONFIG.port}/updatePlayer/${newPlayerElement["playerNum"]}`,
                    data: newData,
                    dataType: "json",
                });
            })

            $("#players").append(newPlayerElement)
        }
    });
}

function updateGame() {
    $.ajax({
        url: `http://${CONFIG.host}:${CONFIG.port}/getGame`
    }).then((data) => {
        gameSystem.receiveGameUpdate(data)
    });
}

function updatePlayer(playerNum) {
    $.ajax({
        url: `http://${CONFIG.host}:${CONFIG.port}/getPlayer/${playerNum}`
    }).then((data) => {
        gameSystem.receivePlayerUpdate(data, playerNum)
    });
}

function receiveEvent(message) {
    console.log("Received event :", message)
    gameSystem.receiveEvent(message);

    let data = JSON.parse(message.data);

    if (data.type == "game") {
        for (let k in data.content) {
            let v = data.content[k];
            $("#game").prop(k, v);
        }
    }
    else if (data.type == "player") {
        let playerElement = playerElementList[data.playerId];

        playerElement["playerNum"] = data.playerId;
        playerElement["playerName"] = data.content.playerName;
        playerElement["role"] = data.content.role;
        playerElement["oxygen"] = data.content.oxygen;
        playerElement["isDead"] = data.content.isDead;
        playerElement["maxOxygen"] = gameSystem.game.maxOxygen;
    }
}


let eventSource = new EventSource(`http://${CONFIG.host}:${CONFIG.port}/notifications_stream`);

eventSource.onmessage = (message) => {
    receiveEvent(message);
};



updateSystem();


// VARS
let then = 0;

function animate(now) {
    now *= 0.001;
    
    const deltaTime = now - then;
    then = now;

    gameSystem.update(deltaTime);
    $("#game").prop("currTime", gameSystem.game.currTime);

    requestAnimationFrame(animate);
}

requestAnimationFrame(animate);
