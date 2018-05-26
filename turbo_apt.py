import os
import urllib
import urllib.parse
from urllib.parse import urlencode, quote_plus
import time
import datetime
import json
import re
from json import JSONEncoder, JSONDecoder
from bs4 import BeautifulSoup
import simplejson

_g_addresses = []

_g_api_key = None

def log(msg, level="info"):
    print(msg)

with open("../personal.json", encoding='utf-8') as f:
   data = json.load(f)
   _g_addresses = data["addresses"]
   #log(_g_addresses)
   _g_api_key = data["google_api_key"]


class EtuoviApt:
    def __init__(self, url, json_file="turbo_apt.json"):
        self.url = url
        self.commute_times = []
        self._html = ""
        self._soup = None
        self.last_updated = 0
        self.address = ""
        if self.load(json_file):
            #The URL was already found from file.
            log("Loaded %s" %(self.address))
        else:
            #This is a new URL. Fetch data and save to file.
            with urllib.request.urlopen(url) as response:
                self._html = response.read()
            self._soup = BeautifulSoup(self._html, 'html.parser')
            #Address of interest
            self.scrapeAddress()
            self.last_updated = time.time()
            for address in _g_addresses:
                trips = {
                    "car": getDistance(self.address, address["address"], "driving"), 
                    "bus": getDistance(self.address, address["address"], "transit")
               }
                self.commute_times.append({
                    "name": address["name"],
                    "trip_choices": trips})
            self.save(json_file)
            
    def scrapeAddress(self):
        map_container = self._soup.find('div', id="mapInfoWindowContent")
        self.address = map_container.find_all('label')[0].get_text()
        log("Address:" + self.address)
        
    def __str__(self):
        string = self.address + "\n"
        for commute in self.commute_times:
            trips = commute["trip_choices"]
            string += "%s is %s (%s by car, %s by bus)" \
                %(commute["name"], trips["car"][0],
                  trips["car"][1], trips["bus"][1]) + "\n"
        string += "Commute estimates are based on the next monday at 8.30"
        return string

    def save(self, filepath):
        """Saves the object to JSON file."""
        
        target = []
        if os.path.exists(filepath):
            with open(filepath, "r") as fp:
                target = json.load(fp)
            for obj in target:
                if type(obj) != dict:
                    raise Exception("Invalid JSON! List contained %s, expected only dict" %(type(obj), ))
                if obj["address"] == self.address:
                    #Remove the existing entry, we'll add it back later.
                    target.remove(obj)
                    log("Removed {}".format(obj["address"]))
            
        tmp_dict = self.__dict__
        #Don't save private keys to file. soup is not serializeable.
        for key in tmp_dict.keys():
            if key.startswith("_"):
                tmp_dict[key] = None
        
        target.append(tmp_dict)

        with open(filepath, "w") as fp:
            fp.write(json.dumps(target, indent=4, sort_keys=True))

    def load(self, filepath):
        """Loads an object from JSON file.
        
        Returns:
            True for existing EtuoviApt objects. Else False."""

        if not os.path.exists(filepath):
            return False
        with open(filepath, "r", encoding="utf-8") as fp:
            json_list = json.load(fp)
        for obj in json_list:
            if "address" in obj and obj["url"] == self.url:
                log("Found match in file for %s" %(self.url))
                for prop in self.__dict__.keys():
                    if not prop.startswith("_"):
                        setattr(self, prop, obj[prop])
                return True
        return False


def getDistance(origin, destination, mode="driving"):
    time_of_travel = int(next_weekday(datetime.datetime.now(), 0, 8, 30).timestamp())
    data = {"origins": origin,
            "departure_time": time_of_travel,
            "destinations": destination,
            "mode": mode,
            "language": "en-EN",
            "key": _g_api_key
           }
    url = "https://maps.googleapis.com/maps/api/distancematrix/json?" + urlencode(data)
    
    try:
        result = simplejson.load(urllib.request.urlopen(url))
    except Exception as e:
        print(url)
        raise e
    try:
        travel_time = result['rows'][0]['elements'][0]['duration']['text']
        friendly_distance = result['rows'][0]['elements'][0]['distance']['text']
        distance = result['rows'][0]['elements'][0]['distance']['value']
    except Exception as e:
        print(result)
        raise e
        
    return friendly_distance, travel_time, distance

def next_weekday(d, weekday, hour, minute):
    """Returns the next weekday datetime at time_of_day"""
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    date = d + datetime.timedelta(days_ahead)
    return datetime.datetime(date.year, date.month, date.day, hour, minute)