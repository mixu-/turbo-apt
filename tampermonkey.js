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
    var send_data = function(data_dict){
        console.log(data_dict);
        GM_xmlhttpRequest({
             method: 'GET',
             url: "http://localhost:8000/add_data?" + $.param(data_dict)
         });
    }

    var GM_addStyle = function(css) {
        const style = document.getElementById("GM_addStyleBy8626") || (function() {
            const style = document.createElement('style');
            style.type = 'text/css';
            style.id = "GM_addStyleBy8626";
            document.head.appendChild(style);
            return style;
        })();
        const sheet = style.sheet;
        sheet.insertRule(css, (sheet.rules || sheet.cssRules || []).length);
    }


    var rate = function(zevent) {
        //console.log(zevent);
        //console.log(zevent.target.id);
        var params = {url: window.location.href};
        var field_name = zevent.target.parentElement.id;
        var rating = $("#" + zevent.target.id).data("number");
        params[field_name] = rating;
        send_data(params);
        if (zevent.target.id.indexOf("toggle") > -1) {
            addToggle(rating, field_name, null, null);
        } else {
            addStars(rating, field_name, null, null);
        }
    };

    GM_addStyle(`.not_selected { font-color: gray; opacity: 0.4; filter: alpha(opacity=40); }`);
    GM_addStyle(`.ratings_header { display: inline-block; text-align: center; position: fixed; bottom: 0; width: 100%; padding: 5px 20%; background: #555; color: #f1f1f1; z-index: 100; font-size: 16px;}`);
    GM_addStyle(`.ratings_header span {float: left; margin: 0.2em 1em;}`);
    GM_addStyle(`.ratings_header span p {font-size: 13px; text-align: left;}`);
    $("body").append('<div class=ratings_header></div>');

    var addStars = function(current_rating, id, title, location) {
        var max_stars = 5;
        if ($("#" + id).length == 0){
            //location, title are only needed when creating a new set of stars.
            $(location).append('<span id="container_' + id + '"><p><strong>' + title + '</strong></p><p id=' + id + '></p></span>');
            console.log("Adding stars for " + id);
        } else { console.log("Updating stars for " + id); }
        $("#" + id).html("");
        for ( var i = 1; i<=max_stars; i++){
            var img_class = "not_selected";
            if (current_rating >= i) {img_class = 'selected'; }
            var stars = '<img data-number="' + i + '" id="' + id + '_star_' + i + '" src="http://localhost:8000/star.png" class="' + img_class + '"/>';
            $("#" + id).append(stars);
            $("#" + id + "_star_" + i).click(rate);
        }
    }
    var addToggle = function(toggle_state, id, title, location) {
        var max_stars = 5;
        if ($("#" + id).length == 0){
            //location, title are only needed when creating a new set of stars.
            $(location).append('<span id="container_' + id + '"><p><strong>' + title + '</strong></p><p id=' + id + '></p></span>');
            console.log("Adding toggle for " + id);
        } else { console.log("Updating toggle for " + id); }
        $("#" + id).html("");
        var img_class = "not_selected";
        if (toggle_state == true) {img_class = 'selected'; }
        var toggle = '<img data-number="' + (!toggle_state).toString() + '" id="' + id + '_toggle" src="http://localhost:8000/x-mark.png" class="' + img_class + '"/>';
        $("#" + id).append(toggle);
        $("#" + id + "_toggle").click(rate);
    }

    var show_data = function(info){
        if (info.length > 0 && info[0].hasOwnProperty("etuovi_additional_info")){
            console.log(info[0]);
            $(".ratings_header").append("<span><p>" + info[0]["etuovi_additional_info"].replace(/(?:\r\n|\r|\n)/g, '<br/>') + "</p></span>");
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
            var info = JSON.parse(response.responseText);
            if (!show_data(info)){
                console.log("No data found yet for this apt. Adding...");
                send_data({url: window.location.href});
                setTimeout(function(){window.location.reload();}, 5000);
            } else {
                console.log("Found apt info from the server already. Using that.");
                var stars = 0;
                var rejected = false;
                if (info[0].hasOwnProperty("fiilis")) { stars = info[0]["fiilis"]; }
                addStars(stars, "fiilis", "Yleisfiilis", ".ratings_header");
                stars = 0;

                if (info[0].hasOwnProperty("kunto")) { stars = info[0]["kunto"]; }
                addStars(stars, "kunto", "Kunto", ".ratings_header");
                stars = 0;

                if (info[0].hasOwnProperty("sijainti")) { stars = info[0]["sijainti"]; }
                addStars(stars, "sijainti", "Sijainti", ".ratings_header");

                if (info[0].hasOwnProperty("hintalaatu")) { stars = info[0]["hintalaatu"]; }
                addStars(stars, "hintalaatu", "Hinta-/Laatusuhde", ".ratings_header");

                if (info[0].hasOwnProperty("rejected")) {
                    rejected = (info[0]["rejected"] == "true");
                }
                addToggle(rejected, "rejected", "Hylätty", ".ratings_header");
            }
        }
    });
}
)();