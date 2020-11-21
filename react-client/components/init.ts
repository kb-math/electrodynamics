import { FrameFetcher } from './FrameFetcher';
import { Plotter } from './Plotter';
import { THREEWrapper } from './THREEWrapper';

export function initClient() {
  const threeObj = new THREEWrapper();
  const plotter = new Plotter(threeObj);

  const frameFetcher = new FrameFetcher(plotter);

  frameFetcher.plotFramesIndefinitely();

  const animate = function () {
    requestAnimationFrame(animate);

    threeObj.renderer.render(threeObj.scene, threeObj.camera);
  };

  animate();
}
