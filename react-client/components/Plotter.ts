import { CircleGeometry, Mesh, MeshBasicMaterial, Object3D, Scene, Vector3 } from 'three';
import { THREEWrapper } from './THREEWrapper';

type ArrayOf3Number = [number, number, number];
type PositionDirectionPair = [ArrayOf3Number, ArrayOf3Number];

export class Plotter {
  private threeWrapper: THREEWrapper;
  private scene: Scene;
  private vectorFieldSamples: Object3D[];
  private pointCharge: Mesh<CircleGeometry, MeshBasicMaterial>;

  constructor(threeWrapper: THREEWrapper) {
    this.threeWrapper = threeWrapper;
    this.scene = threeWrapper.scene;
    this.vectorFieldSamples = [];

    this.pointCharge = this.threeWrapper.createPoint();
    this.scene.add(this.pointCharge);
  }

  public updatePlot(newVectorFieldSamples: PositionDirectionPair[], newChargePosition: ArrayOf3Number): void {
    this.updatePointChargePosition(newChargePosition);
    this.updateVectorFieldSamples(newVectorFieldSamples);
  }

  private updatePointChargePosition(newChargePosition: ArrayOf3Number): void {
    this.pointCharge.position.x = newChargePosition[0];
    this.pointCharge.position.y = newChargePosition[1];
    this.pointCharge.position.z = newChargePosition[2];
  }

  private updateVectorFieldSamples(newVectorFieldSamples: PositionDirectionPair[]): void {
    this.scene.remove(...this.vectorFieldSamples);

    this.vectorFieldSamples = [];

    for (const newSample of newVectorFieldSamples) {
      const origin = new Vector3(newSample[0][0], newSample[0][1], newSample[0][2]);
      const dir = new Vector3(newSample[1][0], newSample[1][1], newSample[1][2]);
      const newArrow = this.threeWrapper.createArrow(origin, dir);

      this.vectorFieldSamples.push(newArrow);
      this.scene.add(newArrow);
    }
  }
}
