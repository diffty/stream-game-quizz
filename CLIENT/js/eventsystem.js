export class EventSystem {
    static _signals = {}

    static connect(signalName, callback) {
        if (typeof callback != "function") {
            throw "Callback arguemnt is not a function";
        }

        if (!(signalName in EventSystem._signals)) {
            EventSystem._signals[signalName] = [];
        }
        EventSystem._signals[signalName].push(callback);
    }

    static emit(signalName, ...callbackArgs) {
        /*if (!(signalName in EventSystem._signals)) {
            console.warn("Signal " + signalName + "not defined");
            return;
        }*/

        if (signalName in EventSystem._signals) {
            EventSystem._signals[signalName].forEach(signalCallback => {
                signalCallback(...callbackArgs);
            });
        }
    }
}
