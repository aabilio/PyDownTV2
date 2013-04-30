function Downloader() {}

Downloader.prototype.downloadFile = function(fileUrl, params, win, fail) {

    //Make params hash optional.
    if (!fail) win = params;
cordova.exec(win, fail, "Downloader", "downloadFile", [fileUrl, params]);
};

window.downloader = new Downloader();