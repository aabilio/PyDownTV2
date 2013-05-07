/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
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
                Lungo.Service.get(pydowntv_api_url+url, null, parsePydowntvAPI, "json");
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
