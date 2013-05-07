/*
	CordovaPlugin (Android): Download Manager (Notification Bar Support)
	Author: aabilio - aabilio[at]gmail.com (@aabilio)
	
	[Based on the following implementations:
		- http://teusink.blogspot.com.es/2013/04/phonegap-android-downloader-plugin.html
		- http://www.toforge.com/2011/02/phonegap-android-plugin-for-download-files-from-url-on-sd-card/
	]

   	Licensed to the Apache Software Foundation (ASF) under one
   	or more contributor license agreements.  See the NOTICE file
   	distributed with this work for additional information
   	regarding copyright ownership.  The ASF licenses this file
   	to you under the Apache License, Version 2.0 (the
   	"License"); you may not use this file except in compliance
   	with the License.  You may obtain a copy of the License at
	
		http://www.apache.org/licenses/LICENSE-2.0
	
	Unless required by applicable law or agreed to in writing,
   	software distributed under the License is distributed on an
   	"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
   	KIND, either express or implied.  See the License for the
   	specific language governing permissions and limitations
   	under the License. 
*/

cordova.define("cordova/plugin/DownloadManager/DownloadManager", function (require, exports, module) {
	var exec = require("cordova/exec");
 	module.exports = {
  		start: function (message, win, fail) {
   			exec(win, fail, "DownloadManager", "start", [message]);
  		},
  		cancel: function (message, win, fail) {
  			exec(win, fail, "DownloadManager", "cancel", [message]);
  		},
  		isdownloading: function (message, win ,fail) {
  			exec(win, fail, "DownloadManager", "isdownloading", [message]);
  		}
 	};
});

var dm = function (action, options, win, fail) {
	var downloader = cordova.require("cordova/plugin/DownloadManager/DownloadManager");
	o = {
		id: options.id || "",
		url: options.url || "",
		filePath: options.filePath || "youraplication",
		fileName: options.fileName || "",
		overwrite: options.overwrite || false,
		useNotificationBar: options.useNotificationBar || true,
		startToast: options.startToast || "Starting download...",
		endToast: options.endToast || "Download end!",
		ticker: options.ticker || "Downloading...",
		notificationTitle: options.notificationTitle || "Downloading...",
		cancelToast: options.cancelToast || "Download canceled!"
	}
	
	if (action == "start") {
		if (o.url == "" ){alert("[ERROR] DownloadManager (JavaScript): URL needed");return -1;}
		downloader.start(o, win, fail);
	} else if (action == "cancel") {
		if (o.id == ""){alert("[ERROR] DownloadManager (JavaScript): ID needed");return -1;}
		downloader.cancel({id: o.id}, win, fail);
	} else if (action == "isdownloading") {
		if (o.id == ""){alert("[ERROR] DownloadManager (JavaScript): ID needed");return -1;}
		downloader.isdownloading({id: o.id}, win, fail);
	} else {
		alert("[ERROR] DownloadManager (JavaScript): Action not supported");
	}
}
window.downloadmanager = dm;
