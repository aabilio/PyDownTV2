/*
    This file is part of pydowntv.

    pydowntv is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    pydowntv is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with pydowntv.  If not, see <http://www.gnu.org/licenses/>.
*/



var app = {
    // Application Constructor
    initialize: function() {
        this.bindEvents();
    },
    // Bind Event Listeners
    //
    // Bind any events that are required on startup. Common events are:
    // 'load', 'deviceready', 'offline', and 'online'.
    bindEvents: function() {
        document.addEventListener('deviceready', this.onDeviceReady, false);
    },
    // deviceready Event Handler
    //
    // The scope of 'this' is the event. In order to call the 'receivedEvent'
    // function, we must explicity call 'app.receivedEvent(...);'
    onDeviceReady: function() {
        app.receivedEvent('deviceready');
        app.searchForIntents();

        // BackButton Event:
        document.addEventListener("backbutton", function(e){
            if(whereIam == "home"){
                e.preventDefault();
                navigator.app.exitApp();
            }
            else {
                Lungo.Router.back();
            }
        }, false);

        Lungo.Router.section('downloads'); // TEMPORAL FIX
        setTimeout(function() {
            Lungo.Router.back();
        }, 50);

    },
    // Update DOM on a Received Event
    receivedEvent: function(id) {
        /*var parentElement = document.getElementById(id);
        var listeningElement = parentElement.querySelector('.listening');
        var receivedElement = parentElement.querySelector('.received');

        listeningElement.setAttribute('style', 'display:none;');
        receivedElement.setAttribute('style', 'display:block;');

        console.log('Received Event: ' + id);*/


        // Callback function for dismissed alert
        /*
        function alertDismissed() {
        }
        navigator.notification.alert(
            'DOM and JavaScrip have loaded!!',  // message
            alertDismissed,                     // callback
            'YummyThings Hello World',          // title
            'I know'                            // buttonName
        );
        */
    },

    searchForIntents: function () {
        /*window.plugins.webintent.getUri(function(url) {
            if(url !== "") {
                // url is the url the intent was launched with
                alert("Esta es la URL: "+url);
            }
            else {
                alert("Hubo un error!");
            }
        });*/
        window.plugins.webintent.getExtra(window.plugins.webintent.EXTRA_TEXT, function (url) {
            //getVideoInfo(url);
            //alert(url);
            if (url === '') {
                Lungo.Notification.error(
                    "Error",                      //Title
                    "Nos has introducido ninguna URL",     //Description
                    "cancel",                     //Icon
                    4,                            //Time on screen
                    null             //Callback function
                );
            } else {
                Lungo.Notification.show();
                $$('#Search4url').val(url);
                Lungo.Service.get(pydowntv_api_url+url, null, function(api) {
                    parsePydowntvAPI(api, url);
                }, "json");
            }
        }, function() { //Fail
            // BETTER NO ERROR!
            /*Lungo.Notification.error(
                "Lo Sentimos",                      //Title
                "No se ha podido capturar el enlace que intentabas compartir con pydowntv",     //Description
                "cancel",                     //Icon
                4,                            //Time on screen
                null             //Callback function
            );*/
        });
    }
};
