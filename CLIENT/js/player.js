export class Player {
    constructor(name, oxygen, isDead, role) {
        this.playerName = name;
        this.oxygen = oxygen;
        this.isDead = isDead;
        this.role = role;
    }

    receiveUpdate(data) {
        for (let k in data) {
            if (k in this) {
                this[k] = data[k];
            }
        }
    }
}
