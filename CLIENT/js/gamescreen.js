import { CONFIG } from '../config.js'

import { EventSystem } from './eventsystem.js';


const EAnswerDisplayMode = {
	UNSELECTED: "summer",
	SELECTED: "winter",
	SOLUTION: "spring",
}


export class GameScreen {
    constructor(game) {
        this.game = game;
        EventSystem.connect("gamescreen_message_received", (payload) => { this.receiveMessage(payload) });
        EventSystem.connect("game_updated", () => { this.onGameUpdate() });
    }
    
    receiveMessage(payload) {
        if (payload.receiver == "gamescreen") {
            if (payload.type == "event") {
                this.receiveEvent(payload);
            }
            else if (payload.type == "data") {
                this.receiveUpdate(payload.data);
            }
        }
    }

    receiveEvent(payload) {
        if (payload.topic == "show_solution") {
            var answerNum = payload.data;
            
            setTimeout(() => {
                this.setAnswerMode(answerNum, EAnswerDisplayMode.SOLUTION);
                setTimeout(() => {
                    this.setAnswerMode(answerNum, this.game.selected_answer_num == answerNum ? EAnswerDisplayMode.SELECTED : EAnswerDisplayMode.UNSELECTED);
                    setTimeout(() => {
                        this.setAnswerMode(answerNum, EAnswerDisplayMode.SOLUTION);
                    }, 150)
                }, 150)
            }, 150)
        }

        else if (payload.topic == "answer_visibility") {
            this.setAnswerVisibility(payload.data.answer_num, payload.data.state);
        }

        else if (payload.topic == "question_changed") {
            for (var i = 0; i < payload.data.answers.length; i++) {
                this.setAnswerContent(i, payload.data.answers[i]);
            }
        }
    }
    
    receiveUpdate(data) {

    }

    setQuestionContent(questionContent) {
        var contents = document.getElementsByClassName("question-text");
        contents[0].textContent = questionContent;
    }

    setAnswerVisibility(answerNum, isVisible) {
        var elements = document.getElementsByClassName("answer-" + "abcd"[answerNum]);
        var contents = elements[0].getElementsByClassName("answer-content");
        contents[0].style = isVisible ? "" : "display: none;";
    }

    setAnswerSelected(answerNum, isSelected) {
        this.setAnswerMode(answerNum, isSelected ? EAnswerDisplayMode.SELECTED : EAnswerDisplayMode.UNSELECTED);
    }

    setAnswerMode(answerNum, answerMode) {
        var elements = document.getElementsByClassName("answer-" + "abcd"[answerNum]);
        
        var contentsBg = elements[0].getElementsByClassName("answer-bg");
        var contentsHead = elements[0].getElementsByClassName("answer-head");
        var contentsText = elements[0].getElementsByClassName("answer-text");

        switch (answerMode) {
            case EAnswerDisplayMode.SELECTED:
                contentsBg[0].style = "background-color: orange;";
                break;

            case EAnswerDisplayMode.UNSELECTED:
                contentsBg[0].style = "background-color: black;";
                break;

            case EAnswerDisplayMode.SOLUTION:
                contentsBg[0].style = "background-color: green;";
                break;
        }

        switch (answerMode) {
            case EAnswerDisplayMode.SELECTED:
            case EAnswerDisplayMode.SOLUTION:
                contentsHead[0].style = "color: white;";
                contentsText[0].style = "color: black;";
            break;

            case EAnswerDisplayMode.UNSELECTED:
                contentsHead[0].style = "color: orange;";
                contentsText[0].style = "color: white;";
        }
    }

    setAnswerContent(answerNum, answerContent) {
        var elements = document.getElementsByClassName("answer-" + "abcd"[answerNum]);
        var contents = elements[0].getElementsByClassName("answer-text");
        contents[0].textContent = answerContent;
    }

    onGameUpdate() {
        console.log(this.game.curr_question_data);
        if (this.game.curr_question_data) {
            this.setQuestionContent(this.game.curr_question_data.question);

            for (var i = 0; i < this.game.curr_question_data.answers.length; i++) {
                this.setAnswerContent(i, this.game.curr_question_data.answers[i]);
                this.setAnswerVisibility(i, this.game.answers_visibility[i]);
                this.setAnswerSelected(i, i == this.game.selected_answer_num);
            }
        }
    }

    update(deltaTime) {
        
    }
}
