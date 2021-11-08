import { GameSystem } from './gamesystem.js'
import { CONFIG } from '../config.js'


// Handle accents
let urlVars = getUrlVars();
var playerNum = null;

export var gameSystem = new GameSystem();

var playerElement = null

// Get custom attributes in URL for custom message
function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        vars[key] = value;
    });
    return vars;
};

function updateSystem() {
    $.ajax({
        url: `http://${CONFIG.host}:${CONFIG.port}/getSystem`
    }).then((data) => {
        gameSystem.receiveSystemUpdate(data)

        $("#players").empty();

        playerElement = null

        for (let k in data.game) {
            let v = data.game[k];
            console.log(k, v);
            $("#game").prop(k, v);
        }

        let newPlayerElement = document.createElement("player-element");

        let p = data.players[playerNum];

        newPlayerElement["playerNum"] = playerNum;
        newPlayerElement["playerName"] = p.playerName;
        newPlayerElement["role"] = p.role;
        newPlayerElement["oxygen"] = p.oxygen;
        newPlayerElement["isDead"] = p.isDead;
        newPlayerElement["maxOxygen"] = gameSystem.game.maxOxygen;

        playerElement = newPlayerElement;

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
    gameSystem.receiveEvent(message);

    let data = JSON.parse(message.data);
    
    if (data.type == "player") {
        if (data.playerId == playerNum) {
            playerElement["playerNum"] = data.playerId;
            playerElement["playerName"] = data.content.playerName;
            playerElement["role"] = data.content.role;
            playerElement["oxygen"] = data.content.oxygen;
            playerElement["isDead"] = data.content.isDead;
            playerElement["maxOxygen"] = gameSystem.game.maxOxygen;
        }
    }
}


if ("playerNum" in urlVars) {
    playerNum = new Number(decodeURI(urlVars["playerNum"]));

    let eventSource = new EventSource(`http://${CONFIG.host}:${CONFIG.port}/notifications_stream`);

    eventSource.onmessage = (message) => {
        receiveEvent(message);
    };

    updateSystem();
}
else {
    console.error("No player id in URL.")
}