
function redirectUrl(url, params={}) {
    for (const key in params) {
        url = url.replace(key, params[key]);
    }
    window.location.replace(url);
}