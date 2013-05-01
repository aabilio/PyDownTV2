cordova.define("cordova/plugin/downloader", function (require, exports, module) {
 var exec = require("cordova/exec");
 module.exports = {
  get: function (message, win, fail) {
   exec(win, fail, "Downloader", "get", [message]);
  }
 };
});