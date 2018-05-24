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
        with urllib.request.urlopen(url) as response:
            self.html = response.read()
        self.soup = BeautifulSoup(self.html, 'html.parser')
        #Address of interest
        self.scrapeAddress()
    
    def scrapeAddress(self):
        map_container = self.soup.find('div', id="mapInfoWindowContent")
        self.address = map_container.find_all('label')[0].get_text()
        
    def __str__(self):
        string = self.address + "\n"
        for address in _g_addresses:
            car = getDistance(self.address, address["address"], "driving")
            bus = getDistance(self.address, address["address"], "transit")
            string += "%s is %s (%s by car, %s by bus)" %(address["name"], car[0], car[1], bus[1]) + "\n"
        string += "Commute estimates are based on the next monday at 8.30"
        return string
       
def getDistance(origin, destination, mode="driving"):
    time_of_travel = next_weekday(datetime.datetime.now(), 0, 8, 30).timestamp()
    # url = "https://maps.googleapis.com/maps/api/distancematrix/json?" \
    #     "origins={0}&destinations={1}&mode={2}&language=en-EN&sensor=false&key={3}" \
    #     .format(urlencode(origin, quote_via=quote_plus), 
    #             urlencode(destination, quote_via=quote_plus), mode, _g_api_key)
    data = {"origins": origin,
            "destinations": destination,
            "mode": mode,
            "language": "en-EN",
            "key": _g_api_key
           }
    url = "https://maps.googleapis.com/maps/api/distancematrix/json?" + urlencode(data)
    
    print(url)
    try:
        result = simplejson.load(urllib.request.urlopen(url))
    except Exception as e:
        print(url)
        raise e
    try:
        travel_time = result['rows'][0]['elements'][0]['duration']['text']
        distance = result['rows'][0]['elements'][0]['distance']['text']
    except Exception as e:
        print(result)
        raise e
        
    return distance, travel_time

def next_weekday(d, weekday, hour, minute):
    """Returns the next weekday datetime at time_of_day"""
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    date = d + datetime.timedelta(days_ahead)
    return datetime.datetime(date.year, date.month, date.day, hour, minute)
    

apt = EtuoviApt("https://www.etuovi.com/kohde/9449326")
print(apt)