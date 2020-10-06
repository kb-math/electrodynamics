function get_request (url, callback) {
    fetch(url).then(callback);
}

function get_json_request(url, callback) {
    get_request(url, 
    async function (response_received) {
        // TODO: deal with non 200 status
        response_received.json().then(function (data) {
            callback(data);
        });
    })
}
