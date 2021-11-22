import * as THREE from './libs/three/build/three.module.js';
import { CONFIG } from '../config.js'

import { EffectComposer } from './libs/three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from './libs/three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPassAlpha } from './postprocessing/UnrealBloomPassAlpha.js';
import { GLTFLoader } from './libs/three/examples/jsm/loaders/GLTFLoader.js';

import { SSAOPass } from './libs/three/examples/jsm/postprocessing/SSAOPass.js';


const renderWidth = 1920;
const renderHeight = 1080;


function findPlayerObject(sceneElement, objectName, objectType) {
    var foundObjects = []

    if (sceneElement.children) {
        for (var i in sceneElement.children) {
            var o = sceneElement.children[i];
            foundObjects = foundObjects.concat(findPlayerObject(o, objectName, objectType));
        }
    }

    if (sceneElement.name.search(objectName) >= 0) {
        if (sceneElement.type == objectType) {
            foundObjects.push(sceneElement);
        }
    }

    return foundObjects;
}


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
        for (let i in this.gameSystem.players) {
            let p = this.gameSystem.players[i];
            this.playerObjects[i]["lifeLight"].visible = p.isDead ? false : true;
            
            let oxyBarTimeMalus = (this.gameSystem.game.maxTime / 60) * (this.gameSystem.game.currTime / this.gameSystem.game.maxTime);

            let oxyBarTargetScale = Math.min(1.0, Math.max(0, ((p.oxygen - oxyBarTimeMalus) / this.gameSystem.game.maxOxygen)));
            let oxyBarDelta = this.playerObjects[i]["oxyMesh"].scale.y - oxyBarTargetScale;

            if (Math.abs(oxyBarDelta) > 0.01) {
                this.playerObjects[i]["oxyMesh"].scale.y -= oxyBarDelta * deltaTime * 3;
            }
            else {
                this.playerObjects[i]["oxyMesh"].scale.y = oxyBarTargetScale;
            }
        }

        if (this.alarmLight) {
            this.alarmLight.visible = this.gameSystem.game.alarm;

            if (this.alarmLEDMesh && this.gameSystem.game.alarm) {
                this.alarmLEDMesh.material.emissive = new THREE.Color(255, 0, 0);
            }
            else {
                this.alarmLEDMesh.material.emissive = new THREE.Color(0, 0, 0);
            }
        }

        if (this.clockNeedle) {
            this.clockNeedle.rotation.x = -(this.gameSystem.game.currTime / this.gameSystem.game.maxTime) * (Math.PI * 2);
        }
        this.cubeCamera.update(this.renderer, this.scene);
    }

    draw(deltaTime) {
        //this.renderer.render(scene, camera);
        this.composer.render();
    }
}
