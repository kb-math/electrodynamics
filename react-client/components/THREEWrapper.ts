import {
  ArrowHelper,
  CircleGeometry,
  Mesh,
  MeshBasicMaterial,
  PerspectiveCamera,
  Scene,
  Vector3,
  WebGLRenderer
} from 'three';

export class THREEWrapper {
  // TODO: make all fields private
  public scene: Scene;
  public camera: PerspectiveCamera;
  public renderer: WebGLRenderer;
  private maxArrowLength: number;
  private arrowColour: number; // hex colour
  private maxHeadLength: number;
  private maxHeadWidth: number;

  constructor() {
    this.scene = new Scene();
    this.camera = new PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);

    this.renderer = new WebGLRenderer();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(this.renderer.domElement);

    // arrow rendering parameters
    this.maxArrowLength = 0.375;
    this.arrowColour = 0xffff00;
    this.maxHeadLength = 0.5 * this.maxArrowLength;
    this.maxHeadWidth = 0.5 * this.maxArrowLength;
    this.camera.position.z = 10;
  }

  // TODO: add args
  public createPoint() {
    const geometry = new CircleGeometry(0.1, 32);
    const material = new MeshBasicMaterial({ color: 0x0000ff });
    const point = new Mesh(geometry, material);

    return point;
  }

  public createArrow(origin: Vector3, dir: Vector3): ArrowHelper {
    const vectorLength = dir.length();
    // convert the vectorLength to a numbers between 0 and 1. That way plotted vector length
    // isn't too large.
    const strengthFactor = 1 - 1 / (1.0 + 100 * Math.log(1 + vectorLength));
    dir.normalize();

    const newArrow = new ArrowHelper(
      dir,
      origin,
      this.maxArrowLength * strengthFactor,
      this.arrowColour,
      this.maxHeadLength * strengthFactor,
      this.maxHeadWidth * strengthFactor
    );
    (newArrow.cone.material as any).opacity = strengthFactor;
    (newArrow.line.material as any).opacity = strengthFactor;
    (newArrow.cone.material as any).transparent = true;
    (newArrow.line.material as any).transparent = true;

    return newArrow;
  }
}
