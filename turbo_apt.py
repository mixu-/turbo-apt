import os
import urllib
import urllib.parse
from urllib.parse import urlencode, quote_plus
import time
import datetime
import json
import pprint
import re
from json import JSONEncoder, JSONDecoder
from bs4 import BeautifulSoup
import simplejson
import googlemaps

_g_addresses = []

maps = None

def log(msg, level="info"):
    print(level + ": " + str(msg))

class EtuoviApt:
    def __init__(self, url, json_file="turbo_apt.json"):
        self.filepath = json_file
        self.url = url
        try:
            self.apt_id = url.rstrip("/").split("/")[-1].split("?")[0]
        except ValueError as e:
            log("Invalid URL: %s" % url)
            raise e
        self.commute_times = []
        self._html = ""
        self._soup = None
        self.last_updated = 0
        self.address = ""
        self.floor = (0, 0)
        self.price_total = 0
        self.price_debt = 0
        self.price_selling = 0
        self.expense_maint = 0
        self.expense_debt = 0
        self.rejected = False
        if os.path.exists(json_file) and self.load(json_file):
            #The URL was already found from file.
            log("Loaded %s" %(self.address))
        else:
            #This is a new URL. Fetch data and save to file.
            with urllib.request.urlopen(url) as response:
                self._html = response.read()
            self._soup = BeautifulSoup(self._html, 'html.parser')
            #Address of interest
            self.scrape()
            coords = map_helper.get_coords(self.address)
            self.coords = (coords["lat"], coords["lng"])
            self.last_updated = time.time()
            for address in _g_addresses:
                trips = {
                    "car": map_helper.get_distance(self.address, address["address"], "driving"), 
                    "bus": map_helper.get_distance(self.address, address["address"], "transit")
               }
                self.commute_times.append({
                    "name": address["name"],
                    "trip_choices": trips})
            self.save(json_file)
    
    def scrape(self):
        def scrape_price(self, field_name):
            try:
                self.price_selling = float(soup.find('dt', text=field_name)\
                    .find_next_sibling().get_text().strip().replace("€", "").replace(" ", "").replace(",", "."))
                return True
            except AttributeError:
                log("%s not found" %field_name)
            return False        
        #Address
        soup = self._soup
        map_container = soup.find('div', id="mapInfoWindowContent")
        self.address = map_container.find_all('label')[0].get_text()
        log("Address:" + self.address)

        #Floor        
        basics = soup.find('article', class_="basics").find("dl")
        self.floor_raw = basics.find('dt', text="Kerrokset:").find_next_sibling().get_text()
        if self.floor_raw and "/" in self.floor_raw:
            self.floor = tuple(self.floor_raw.split("/"))

        #Price
        if not scrape_price(self, "Myyntihinta:"):
            if not scrape_price(self, "Velaton lähtöhinta:"):
                if not scrape_price(self, "Viimeisin tarjous:"):
                    log("Failed to find the price for this place.")
                    self.price_selling = 0

        try:
            self.price_debt = float(soup.find('dt', text="Velkaosuus:")
                .find_next_sibling().get_text().strip().replace("€", "").replace(" ", "").replace(",", "."))
        except AttributeError:
            log("Debt price not found. Assuming 0.")
            self.price_debt = 0
        self.price_total = self.price_debt + self.price_selling

        #Monthly costs
        maint_cost = soup.find(string=re.compile("Hoitovastike"))
        if maint_cost:
            match = re.match(r".*Hoitovastike (\d{0,7},\d{1,2}).*Rahoitusvastike (\d{0,7},\d{1,2})", maint_cost)
            if match:
                self.expense_maint = float(match.group(1).replace(",", "."))
                self.expense_debt = float(match.group(2).replace(",", "."))
        
    def __str__(self):
        string = "\n***************************\n" + self.address + "\n"
        string += "Price: {} € ({} € + {} € of debt) €\n"\
            .format(self.price_total, self.price_selling, self.price_debt)
        string += "Expenses: {}/{}\n".format(self.expense_maint, self.expense_debt)
        string += "Floor: {}/{}\n".format(self.floor[0], self.floor[1])
        for commute in self.commute_times:
            trips = commute["trip_choices"]
            string += "%s is %s (%s by car, %s by bus)" \
                %(commute["name"], trips["car"][0],
                  trips["car"][1], trips["bus"][1]) + "\n"
        string += "Commute estimates are based on the next monday at 8.30\n"
        string += "\nOther information:\n"
        already_printed = ["address", "price_debt", "price_selling", "price_total",
                           "expense_maint", "expense_debt", "floor", "commute_times",
                           "floor_raw", "_soup", "_html", "last_updated"]
        for key, value in self.__dict__.items():
            if key not in already_printed and not key.startswith("_"):
                string += "%s: %s\n" %(key, value, )
        return string

    def get_etuovi_info_str(self):

        string = ""
        for commute in self.commute_times:
            trips = commute["trip_choices"]
            string += "%s is %s (%s by car, %s by bus)" \
                %(commute["name"], trips["car"][0],
                  trips["car"][1], trips["bus"][1]) + "\n"
        string += "Commute estimates are based on the next monday at 8.30\n"
        return string

    def save(self, filepath=None):
        """Saves the object to JSON file."""
        if not filepath:
            filepath = self.filepath
        log("Saving to file...")
        target = []
        apt_from_file = {}
        if os.path.exists(filepath):
            with open(filepath, "r") as fp:
                target = json.load(fp)
            for obj in target:
                if type(obj) != dict:
                    raise Exception("Invalid JSON! List contained %s, expected only dict" %(type(obj), ))
                if obj["address"] == self.address:
                    #Remove the existing entry, we'll add it back later.
                    apt_from_file = obj.copy()
                    target.remove(obj)
                    log("Removed {}".format(obj["address"]))
            
        #Merge dictionaries
        tmp_dict = {**apt_from_file, **self.__dict__.copy()}
        #Don't save private keys to file. soup is not serializeable.
        for key in self.__dict__.keys():
            if key.startswith("_"):
                tmp_dict.pop(key)
        tmp_dict["etuovi_additional_info"] = self.get_etuovi_info_str()
        target.append(tmp_dict)
        #log(pprint.pformat(target))
        with open(filepath, "w") as fp:
            fp.write(json.dumps(target, indent=4, sort_keys=True))

    def load(self, filepath=None):
        """Loads an object from JSON file.
        
        Returns:
            True for existing EtuoviApt objects. Else False."""

        if not filepath:
            filepath = self.filepath
        if not os.path.exists(filepath):
            return False
        with open(filepath, "r", encoding="utf-8") as fp:
            json_list = json.load(fp)
        try:
            for obj in json_list:
                if "address" in obj and obj["apt_id"] == self.apt_id:
                    log("Found match in file for %s" %(self.apt_id))
                    for prop in self.__dict__.keys():
                        if not prop.startswith("_"):
                            setattr(self, prop, obj[prop])
                    return True
        except Exception:
            log("Failed to load EtuoviApt from file.")
            return False
        return False

class MapHelper():
    def __init__(self, maps):
        self.maps = maps

    def get_coords(self, address):
        """Converts an address to lat, lng dict"""
        geocode = self.maps.geocode(address)[0]
        return geocode["geometry"]["location"]

    def get_distance(self, origin, destination, mode="driving"):
        time_of_travel = int(next_weekday(datetime.datetime.now(), 0, 8, 30).timestamp())
        kwargs = {
            "origins": origin,
            "departure_time": time_of_travel,
            "destinations": destination,
            "mode": mode,
            "language": "en-EN",
        }
        
        result = self.maps.distance_matrix(**kwargs)
        #log(pprint.pformat(result))
        try:
            if result["rows"][0]["elements"][0]['status'] == "OK":
                travel_time = result['rows'][0]['elements'][0]['duration']['text']
                friendly_distance = result['rows'][0]['elements'][0]['distance']['text']
                distance = result['rows'][0]['elements'][0]['distance']['value']
            else:
                log("Warning: Google Maps was unable to calculate distance!")
                return None, None, None
        except KeyError as e:
            log("Invalid response!", "ERROR")
            log(pprint.pformat(result), "ERROR")
            raise e
            
        return friendly_distance, travel_time, distance

def next_weekday(d, weekday, hour, minute):
    """Returns the next weekday datetime at time_of_day"""
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    date = d + datetime.timedelta(days_ahead)
    return datetime.datetime(date.year, date.month, date.day, hour, minute)


with open("../personal.json", encoding='utf-8') as f:
    data = json.load(f)
    _g_addresses = data["addresses"]
    maps = googlemaps.Client(key=data["google_api_key"])
    map_helper = MapHelper(maps)
