const trajectoryUrl = 'http://localhost:5000/trajectory';
export function createFrameBufferUrl(duration: number, dt: number): string {
  var url = trajectoryUrl;

  url += '?';
  url += 'dt=' + dt.toString();
  url += '&';
  url += 'duration=' + duration.toString();

  return url;
}
