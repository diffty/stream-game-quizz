import { CONFIG } from '../config.js'

import { GameScreen } from './gamescreen.js'
import { GameSystem } from './gamesystem.js'
import { EventSystem } from './eventsystem.js';


let then = 0;

var gameSystem = new GameSystem();
var gameScreen = new GameScreen(gameSystem.game);

let eventSource = new EventSource(`http://192.168.1.47:${CONFIG.port}/notifications_stream`);

eventSource.onmessage = (message) => {
    let payload = JSON.parse(message.data);
    console.log(payload);
    EventSystem.emit(`${payload.receiver}_message_received`, payload)
};

function animate(now) {
    now *= 0.001;
    
    const deltaTime = now - then;
    then = now;

    gameSystem.update(deltaTime);
    gameScreen.update(deltaTime);

    requestAnimationFrame(animate);

}

requestAnimationFrame(animate);
