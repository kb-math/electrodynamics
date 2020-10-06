class THREEJSWrapper {
    constructor() {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 );
        
        this.renderer = new THREE.WebGLRenderer();
        this.renderer.setSize( window.innerWidth, window.innerHeight );
        document.body.appendChild( this.renderer.domElement );
        
        // arrow rendering parameters
        this.maxArrowLength = 0.375;
        this.arrowColour = 0xffff00;
        this.maxHeadLength = 0.5 * this.maxArrowLength;
        this.maxHeadWidth = 0.5 * this.maxArrowLength;
        this.camera.position.z = 10;
    }

    // TODO: add args
    createPoint() {
        const geometry = new THREE.CircleGeometry( 0.1, 32 );
        const material = new THREE.MeshBasicMaterial( { color: 0x0000FF} );
        var point = new THREE.Mesh( geometry, material );

        return point;
    }

    createArrow(origin, dir) {
        var vectorLength = dir.length();
        // convert the vectorLength to a number between 0 and 1. That way plotted vector length
        // isn't too large.
        var strengthFactor = 1 - 1/(1.0 + 100*Math.log(1 + vectorLength))
        dir.normalize();
    
        var newArrow = new THREE.ArrowHelper(dir, origin, this.maxArrowLength * strengthFactor, this.arrowColour, 
            this.maxHeadLength * strengthFactor, this.maxHeadWidth * strengthFactor);
        newArrow.cone.material.opacity = strengthFactor;
        newArrow.line.material.opacity = strengthFactor;
        newArrow.cone.material.transparent = true;
        newArrow.line.material.transparent = true;

        return newArrow;
    }
}
class Plotter {
    constructor(THREEJSWrapper) {
        this.THREEJSWrapper = THREEJSWrapper;
        this.scene = THREEJSWrapper.scene
        this.vectorFieldSamples = [];

        this.pointCharge = this.THREEJSWrapper.createPoint();
        this.scene.add( this.pointCharge );
    }
    
    updatePointChargePosition(newChargePosition) {
        this.pointCharge.position.x = newChargePosition[0];
        this.pointCharge.position.y = newChargePosition[1];
        this.pointCharge.position.z = newChargePosition[2];
    }
    
    updateVectorFieldSamples(newVectorFieldSamples) {
        for (var arrow of this.vectorFieldSamples) {
            this.scene.remove(arrow);
        };
        
        this.vectorFieldSamples = [];
        
        for (var newSample of newVectorFieldSamples) {
            var origin = new THREE.Vector3(newSample[0][0], newSample[0][1], newSample[0][2]);
            var dir = new THREE.Vector3(newSample[1][0], newSample[1][1], newSample[1][2]);
            var newArrow = this.THREEJSWrapper.createArrow(origin, dir);
        
            this.vectorFieldSamples.push(newArrow);
            this.scene.add(newArrow);
        }

    }

    updatePlot(newVectorFieldSamples, newChargePosition) {
        this.updatePointChargePosition(newChargePosition);
        this.updateVectorFieldSamples(newVectorFieldSamples);

    }
}

const trajectoryUrl = "http://localhost:5000/trajectory"
function createFrameBufferUrl(duration, dt) {
    var url = trajectoryUrl;

    url += "?";
    url += "dt=" + dt.toString();
    url += "&";
    url += "duration=" + duration.toString();

    return url;
}

class FrameFetcher {
    constructor(plotter) {
        this.plotter = plotter;

        this.backFrameBuffer = null;
        this.frontFrameBuffer = null;

        this.lastPlotTime = null;
        this.ffwRate = 4.0;

        this.duration = 20.0;
        this.dt = 0.5;
    }

    async plotFramesIndefinitely() {
        this.getNextBuffer();

        while (true) {
            await this.plotFrontBufferContinuously();
        }
    }

    async plotFrontBufferContinuously() {
        while (this.backFrameBuffer == null) {
            console.log("waiting for a backFrameBuffer!");
            await sleep(100);
        }

        this.frontFrameBuffer = this.backFrameBuffer;
        this.backFrameBuffer = null;

        this.getNextBuffer();

        for (var frame of this.frontFrameBuffer) {
            var nextPlotTime = frame[0];
            if (this.lastPlotTime != null) {
                await sleep(1000*(nextPlotTime - this.lastPlotTime) / this.ffwRate);
            }
            this.lastPlotTime = nextPlotTime;

            this.plotter.updatePlot(frame[2], frame[1]);
        }
    }

    setBack(next_frame_buffer) {
        this.backFrameBuffer = next_frame_buffer;
    }

    async getNextBuffer() {
        var frame_buffer = null;
        var this_ = this;

        get_json_request(createFrameBufferUrl(this.duration, this.dt),
            async function (data) {
                // TODO: deal with non 200 status
                frame_buffer = data;
                this_.backFrameBuffer = frame_buffer;
            }
        );
    }
}

function initClient() {
    THREEJS = new THREEJSWrapper()
    const plotter = new Plotter(THREEJS);
    
    const frameFetcher = new FrameFetcher(plotter);
    
    frameFetcher.plotFramesIndefinitely();
    
    const animate = function () {
        requestAnimationFrame( animate );
    
        THREEJS.renderer.render( THREEJS.scene, THREEJS.camera );
    
    };
    
    animate();

}

initClient();

