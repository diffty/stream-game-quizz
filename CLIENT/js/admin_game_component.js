import { LitElement, html, css } from 'https://unpkg.com/lit-element/lit-element.js?module';
import { CONFIG } from '../config.js'


function getFormattedTime(timestamp) {
    let hours = Math.floor(timestamp / 3600) % 24;
    let minutes = Math.floor(timestamp / 60) % 60;
    let seconds = Math.floor(timestamp) % 60;
    return `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`
}

export class GameAdminElement extends LitElement {
    constructor() {
        super()
        
    }

    static get properties() {
        return {
            alarm: {type: Boolean},
            currTime: {type: String},
            maxTime: {type: Number},
        }
    }
        
    static get styles() {
        return css`.mood { color: green; }`;
    }

    onCurrTimeChanged(e) {
        console.log("changed")
        let propertyName = e.target.id;
        this.currTime = e.target.value;
        this.onPropertyChanged(propertyName, e.target.value);
    }
    
    onMaxTimeChanged(e) {
        let propertyName = e.target.id;
        this.maxTime = e.target.value;
        this.onPropertyChanged(propertyName, e.target.value);
    }
    
    onAlarmChanged(e) {
        console.log(e);
        let propertyName = e.target.id;
        this.alarm = e.target.checked;
        console.log(e.target.checked)
        this.onPropertyChanged(propertyName, e.target.checked);
    }

    onPropertyChanged(propertyName, newValue) {
        let gameChangedEvent = new CustomEvent('changed', { 
            detail: { "propertyName": propertyName, "newValue": newValue },
            bubbles: true, 
            composed: true
        });

        this.dispatchEvent(gameChangedEvent);
    }

    onStartButtonClick() {
        $.get({
            url: `http://${CONFIG.host}:${CONFIG.port}/start`,
        })
    }

    onPauseButtonClick() {
        $.get({
            url: `http://${CONFIG.host}:${CONFIG.port}/pause`,
        })
    }

    onResetButtonClick() {
        $.get({
            url: `http://${CONFIG.host}:${CONFIG.port}/reset`,
        })
    }

    render() {
        return html`
        <li>
            <h2>Game</h2>
            <ul>
                <li>Elapsed : ${getFormattedTime(this.currTime)}</li>
                <li>Remaining : ${getFormattedTime(this.maxTime - this.currTime)}</li>
                <li>Curr Time : <input id="currTime" .value=${Math.floor(this.currTime)} @change="${this.onCurrTimeChanged}" /></li>
                <li>Max Time : <input id="maxTime" .value=${this.maxTime} @change="${this.onMaxTimeChanged}" /></li>
                <li>Alarm ? <input id="alarm" ?checked=${this.alarm} type="checkbox" @change="${this.onAlarmChanged}" /></li>
                <button @click="${this.onStartButtonClick}">Start</button>
                <button @click="${this.onPauseButtonClick}">Pause</button>
                <button @click="${this.onResetButtonClick}">Reset</button>
            </ul>
        </li>
        `;
    }
};

customElements.define('game-admin-element', GameAdminElement);
