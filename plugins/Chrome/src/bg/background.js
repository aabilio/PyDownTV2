// if you checked "fancy-settings" in extensionizr.com, uncomment this lines

// var settings = new Store("settings", {
//     "sample_setting": "This is how you use Store.js to remember values"
// });



//example of using a message handler from the inject scripts
chrome.extension.onMessage.addListener(
  function(request, sender, sendResponse) {
  	chrome.pageAction.show(sender.tab.id);
    sendResponse();
  });

chrome.browserAction.onClicked.addListener(function (tab) {
	chrome.tabs.query({"active": true}, function(tab){
    	//alert(tab[0].url);  //selected tab
    	var url = "http://web.pydowntv.com/?url="+escape(tab[0].url)
    	var ventana = window.open(url);
	});
});