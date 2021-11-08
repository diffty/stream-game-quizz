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

        // LOADING TEXTURES
        var texloader = new THREE.TextureLoader();
        var clock = new THREE.Clock();
        var gltfLoader = new GLTFLoader();

        // SCENE & CAM
        this.scene = new THREE.Scene();
        this.camera = null;

        // RENDERER
        this.renderer = new THREE.WebGLRenderer( { alpha: true, antialias: true } );
        this.renderer.setSize( renderWidth, renderHeight );
        this.renderer.setClearColor( 0x000000, 0 ); // the default
        document.body.appendChild( this.renderer.domElement );

        // ******** SHADER SHIT ********
        this.composer = new EffectComposer(this.renderer);

        // CUBE MAP
        const cubeRenderTarget = new THREE.WebGLCubeRenderTarget( 128, { format: THREE.RGBFormat, generateMipmaps: true, minFilter: THREE.LinearMipmapLinearFilter } );
        this.cubeCamera = new THREE.CubeCamera(0.1, 100000, cubeRenderTarget); 
        this.cubeCamera.position.x += 8;
        this.scene.add(this.cubeCamera);

        // Asset loading
        this.playerObjects = [];
        this.alarmLight = null;

        gltfLoader.load(
            "./models/overlay.gltf",
            (gltf) => {
                this.scene.add(gltf.scene);

                this.camera = gltf.cameras[0];
                this.camera.aspect = 1.778;
                this.camera.updateProjectionMatrix();

                this.alarmLight = findPlayerObject(this.scene, "_Alarm", "PointLight")[0];
                this.alarmLEDMesh = findPlayerObject(this.scene, "_AlarmLED", "Mesh")[0];
                this.clockNeedle = findPlayerObject(this.scene, "_Clock", "Mesh")[0];
                this.oxyMeterGlass = findPlayerObject(this.scene, "_OxygenMeter_Glass", "Mesh")[0];
                
                this.oxyMeterGlass.material.envMap = this.cubeCamera.renderTarget.texture;
                this.oxyMeterGlass.material.reflectivity = 1.0;

                for (var i = 0; i < 4; i++) {
                    let lifeLight = findPlayerObject(this.scene, "_Life_P" + (i+1), "SpotLight");
                    let oxyMesh = findPlayerObject(this.scene, "_OxygenMeter_P" + (i+1), "Mesh");
                    let envMesh = findPlayerObject(this.scene, "_EnvSphere", "Mesh");
                    let oxyPipeMesh = findPlayerObject(this.scene, "_OxygenPipe", "Mesh");
                    let hublotsMesh = findPlayerObject(this.scene, "_Hublots", "Mesh");
                    let bgMesh = findPlayerObject(this.scene, "_Fond", "Mesh");
                    let clockEdgeMesh = findPlayerObject(this.scene, "_ClockEdge", "Mesh");

                    envMesh[0].material.emissive = new THREE.Color(1, 1, 1);
                    envMesh[0].material.emissiveMap = envMesh[0].material.map;
                    envMesh[0].material.emissiveIntensity = 2;

                    // Tweaking Oxygen Bars
                    oxyMesh[0].material.emissive = new THREE.Color(0.0, 0.376085, 1);
                    oxyMesh[0].material.emissiveIntensity = 1.2;

                    oxyPipeMesh[0].material.envMap = this.cubeCamera.renderTarget.texture;
                    hublotsMesh[0].material.envMap = this.cubeCamera.renderTarget.texture;
                    bgMesh[0].material.envMap = this.cubeCamera.renderTarget.texture;
                    clockEdgeMesh[0].material.envMap = this.cubeCamera.renderTarget.texture;

                    this.playerObjects.push({
                        "lifeLight": lifeLight[0],
                        "oxyMesh": oxyMesh[0],
                    });
                }

                this.receiveSystemUpdate();
                
                this.renderPass = new RenderPass( this.scene, this.camera );
                this.renderPass.clearAlpha = 0;
                
                this.composer.addPass( this.renderPass );

                //const ssaoPass = new SSAOPass( this.scene, this.camera, renderWidth, renderHeight );
                //ssaoPass.kernelRadius = 16;
                //ssaoPass.minDistance =  0.02 ;
                //ssaoPass.maxDistance = 0.3 ;
                //ssaoPass.output = SSAOPass.OUTPUT.Beauty;

                //this.composer.addPass( ssaoPass );
            }
        )

        var bloomPass = new UnrealBloomPassAlpha( new THREE.Vector2( renderWidth, renderHeight ), 1.5, 0.4, 0.85 );
        bloomPass.threshold = 0.0;
        bloomPass.strength = 2.0;
        bloomPass.radius = 1.0;
        this.composer.addPass( bloomPass );


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
