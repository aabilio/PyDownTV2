/*
 * PhoneGap is available under *either* the terms of the modified BSD license *or* the
 * MIT License (2008). See http://opensource.org/licenses/alphabetical for full text.
 *
 * Copyright (c) 2005-2010, Nitobi Software Inc.
 * Copyright (c) 2011, IBM Corporation
 */

/**
 * Constructor
 */
function Thumbnailer() {
};

/**
 * Starts the video player intent
 *
 * @param url           The url to play
 */
Thumbnailer.prototype.createVideoThumbnail = function(url, callback) {
	if (url.toLowerCase().indexOf("file://")==0){
		url =url.substring(7); 
	}
    cordova.exec(callback, thumbError, "Thumbnailer", "createVideoThumbnail", [url]);
};
Thumbnailer.prototype.createImageThumbnail = function(url, callback) {
	if (url.toLowerCase().indexOf("file://")==0){
		url =url.substring(7); 
	}
    cordova.exec(callback, thumbError, "Thumbnailer", "createImageThumbnail", [url]);
};

function thumbError(err){
	alert('Error creating thumbnail!');
};

/**
 * Load Thumbnailer
 */

if(!window.plugins) {
    window.plugins = {};
}
if (!window.plugins.thumbnailer) {
    window.plugins.thumbnailer = new Thumbnailer();
}
