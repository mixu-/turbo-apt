// ==UserScript==
// @name         TurboApt for Etuovi.com
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @match        https://www.etuovi.com/kohde/*
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
             url: "http://localhost:8000/add_data?" + $.param(data_dict)
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
    <div id="turbo_apt_info">
    </div>
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

    var show_data = function(data){
        var info = JSON.parse(data);
        if (info.length > 0 && info[0].hasOwnProperty("etuovi_additional_info")){
            console.log(info[0]);
            $("#turbo_apt_info").html("<p>" + info[0]["etuovi_additional_info"].replace(/(?:\r\n|\r|\n)/g, '<br/>') + "</p>");
            return true;
        }
        return false;
    }

    var array = window.location.href.split("/");
    var url = 'http://localhost:8000/get_data?apt_id=' + array[array.length-1].split("?")[0];
    GM_xmlhttpRequest({
        method: 'GET',
        url: url,
        onload: function(response) {
            if (!show_data(response.responseText)){
                console.log("No data found yet for this apt. Adding...");
                send_data({url: window.location.href});
            } else {
                console.log("Found apt info from the server already. Using that.");
            }
        }
    });
}
)();