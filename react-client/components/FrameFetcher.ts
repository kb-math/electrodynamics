import { Plotter } from './Plotter';
import { createFrameBufferUrl, getJsonRequest, sleep } from './requestUtils';
import { FrameData } from './types';

export class FrameFetcher {
  private plotter: Plotter;
  private backFrameBuffer: FrameData[] | null;
  private frontFrameBuffer: FrameData[] | null;
  private duration: number;
  private ffwRate: number;
  private dt: number;
  private lastPlotTime: number | null;

  constructor(plotter: Plotter) {
    this.plotter = plotter;

    this.backFrameBuffer = null;
    this.frontFrameBuffer = null;

    this.lastPlotTime = null;
    this.ffwRate = 4.0;

    this.duration = 20.0;
    this.dt = 0.5;
  }

  public async plotFramesIndefinitely(): Promise<void> {
    this.getNextBuffer();

    // eslint-disable-next-line no-constant-condition
    while (true) {
      await this.plotFrontBufferContinuously();
    }
  }

  private async plotFrontBufferContinuously() {
    while (this.backFrameBuffer == null) {
      console.log('waiting for a backFrameBuffer!');
      await sleep(100);
    }

    this.frontFrameBuffer = this.backFrameBuffer;
    this.backFrameBuffer = null;

    this.getNextBuffer();

    for (const frame of this.frontFrameBuffer) {
      const nextPlotTime = frame[0];
      if (this.lastPlotTime != null) {
        await sleep((1000 * (nextPlotTime - this.lastPlotTime)) / this.ffwRate);
      }
      this.lastPlotTime = nextPlotTime;

      this.plotter.updatePlot(frame[2], frame[1]);
    }
  }

  private setBack(nextFrameBuffer: FrameData[]): void {
    this.backFrameBuffer = nextFrameBuffer;
  }

  private async getNextBuffer(): Promise<void> {
    getJsonRequest(createFrameBufferUrl(this.duration, this.dt), (data: FrameData[]) => {
      this.setBack(data);
    });
  }
}
