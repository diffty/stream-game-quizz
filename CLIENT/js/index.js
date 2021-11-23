import { GameScreen } from './gamescreen.js'
import { GameSystem } from './gamesystem.js'
import { CONFIG } from '../config.js'


// VARS
let then = 0;

var gameSystem = new GameSystem();
var gameScreen = new GameScreen(gameSystem);


let eventSource = new EventSource(`http://${CONFIG.host}:${CONFIG.port}/notifications_stream`);

eventSource.onmessage = (message) => {
    gameSystem.receiveEvent(message);
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
