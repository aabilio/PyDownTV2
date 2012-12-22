const widgets = require("widget");
const tabs = require("tabs");

var widget = widgets.Widget({
  id: "pydowntv-link",
  label: "Buscar en pydowntv",
  contentURL: "http://web.pydowntv.com/static/img/favicon_black.ico",
  onClick: function() {
      tabUrl = tabs.activeTab.url;
    if (tabUrl.search("rtpa.es") != -1)
    {
      tabUrl = escape(tabUrl);
    }
    var url = "http://web.pydowntv.com/?url="+tabUrl;
    
    tabs.open(url);
  }
});

console.log("The add-on is running.");