// ==UserScript==
// @name         TurboApt for Etuovi.com
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @match        https://www.etuovi.com/*
// @grant        GM_xmlhttpRequest
// @require  http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js
// ==/UserScript==

(function() {
    'use strict';
    //GM_addStyle('.not_selected { font-color: gray; }');
    var send_data = function(data_dict){
        console.log(data_dict);
        GM_xmlhttpRequest({
             method: 'GET',
             url: "http://localhost:8000/?" + $.param(data_dict)
         });
    }

    var rate = function(zevent) {
        console.log(zevent.target.parent);
        var params = {url: window.location.href};
        if (zevent.target.id.indexOf("bad") > -1) {
            params["rating"] = "bad";
            send_data(params);
        }
        if (zevent.target.id.indexOf("good") > -1) {
            params["rating"] = "good";
            send_data();
        }
        if (zevent.target.id.indexOf("great") > -1) {
            params["rating"] = "great";
            send_data(params);
        }
        if (zevent.target.id.indexOf("renovations") > -1) {
            params["renovations"] = zevent.target.id;
            send_data(params);
        }
    };
    $(".description").prepend ( `
    <div id="rating">
        <p><strong>Yleisfiilis</strong></p>
        <p id="bad" class="not_selected">Huono</p>
        <p id="good" class="not_selected">Hyvä</p>
        <p id="great" class="not_selected">Mahtava</p>
    </div>` );

    $("#bad").click(rate);
    $("#good").click(rate);
    $("#great").click(rate);
    $(".project").prepend ( `
    <div id="renovations">
        <p><strong>Tulevat remontit</strong></p>
        <p id="big_renovations" class="not_selected">Iso yhtiöremontti</p>
        <p id="small_renovations" class="not_selected">Pieni yhtiöremontti</p>
        <p id="no_renovations" class="not_selected">Ei remontteja</p>
    </div>` );
    $("#big_renovations").click(rate);
    $("#small_renovations").click(rate);
    $("#no_renovations").click(rate);
}
)();