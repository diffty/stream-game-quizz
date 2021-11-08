export class Game {
    constructor() {
        this.alarm = false;
        this.currTime = 0;
        this.maxTime = 3600;
        this.maxOxygen = 75;
        this.isTimerActive = false;
        this.isGameEnded = true;
        this.isGameStarted = false;
    }

    setTime(t) {
        this.currTime = t;
    }

    start() {
        this.isTimerActive = true;
    }

    pause() {
        this.isTimerActive = false;
    }

    update(deltaTime) {
        if (this.isTimerActive) {
            this.currTime += deltaTime;
        }
    }

    receiveUpdate(data) {
        for (let k in data) {
            if (k in this) {
                this[k] = data[k];
            }
        }
    }
}
