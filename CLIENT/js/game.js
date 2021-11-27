import { EventSystem } from './eventsystem.js';


export class Game {
    constructor() {
        EventSystem.connect("game_message_received", (payload) => { this.receiveMessage(payload) });

        this.curr_question_id = 0;
        this.curr_question_data = {};
        this._curr_question_obj = null;
        this.selected_answer_num = -1;
        
        this.answers_visibility = []
        
        this.curr_question_time = 0;
        this.max_question_time = 30;

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

    receiveMessage(payload) {
        if (payload.receiver == "game") {
            if (payload.type == "event") {
                this.receiveEvent(payload);
            }
            else if (payload.type == "data") {
                this.receiveUpdate(payload.data);
            }
        }
    }

    receiveEvent(payload) {
        if (payload.topic == "question_changed") {

        }
    }

    receiveUpdate(data) {
        for (let k in data) {
            if (k in this) {
                this[k] = data[k];
            }
        }
        EventSystem.emit("game_updated");
    }
}
