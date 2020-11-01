function getRequest(url: string, callback: any): void {
  fetch(url).then(callback);
}

export function getJsonRequest(url: string, callback: any): void {
  getRequest(url, async function (response_received: any) {
    // TODO: deal with non 200 status
    response_received.json().then(function (data: any) {
      callback(data);
    });
  });
}
