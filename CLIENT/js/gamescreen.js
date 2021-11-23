import { CONFIG } from '../config.js'


export class GameScreen {
    constructor(gameSystem) {
        this.gameSystem = gameSystem;

        this.receiveSystemUpdate();
    }

    receiveSystemUpdate() {
        $.ajax({
            url: `http://${CONFIG.host}:${CONFIG.port}/getSystem`
        }).then((data) => {
            this.gameSystem.receiveSystemUpdate(data)
        });
    }

    update(deltaTime) {
        
    }
}
