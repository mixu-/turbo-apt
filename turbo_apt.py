import urllib
import urllib.parse
from urllib.parse import urlencode, quote_plus
import datetime
import json
from bs4 import BeautifulSoup
import simplejson

_g_addresses = []

_g_api_key = None

with open("../personal.json", encoding='utf-8') as f:
   data = json.load(f)
   _g_addresses = data["addresses"]
   print(_g_addresses)
   _g_api_key = data["google_api_key"]


class EtuoviApt:
    def __init__(self, url):
        self.url = url
        if self.load():
            #The URL was already found from file.
            pass
        else:
            #This is a new URL. Fetch data and save to file.
            with urllib.request.urlopen(url) as response:
                self.html = response.read()
            self.soup = BeautifulSoup(self.html, 'html.parser')
            #Address of interest
            self.scrapeAddress()
            self.commute_times = []
            for address in _g_addresses:
                trips = {
                    "car": getDistance(self.address, address["address"], "driving"), 
                    "bus": getDistance(self.address, address["address"], "transit")
                }
                self.commute_times.append({
                    "name": address["name"],
                    "trip_choices": trips})
            self.save()
            
    def scrapeAddress(self):
        map_container = self.soup.find('div', id="mapInfoWindowContent")
        self.address = map_container.find_all('label')[0].get_text()
        
    def __str__(self):
        string = self.address + "\n"
        for commute in self.commute_times:
            trips = commute["trip_choices"]
            string += "%s is %s (%s by car, %s by bus)" \
                %(commute["name"], trips["car"][0],
                  trips["car"][1], trips["bus"][1]) + "\n"
        string += "Commute estimates are based on the next monday at 8.30"
        return string

    def save(self):
        """TODO: Saves the object to JSON file."""
        return

    def load(self):
        """TODO: Loads an object from JSON file.
        
        Returns:
            True for existing EtuoviApt objects. Else False."""
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