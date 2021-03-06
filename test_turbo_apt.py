import unittest
import pprint
import os
import json
import turbo_apt
from turbo_apt import map_helper
from turbo_apt import EtuoviApt

_g_jsonfile = "test.json"
_g_test_urls = ["https://www.etuovi.com/kohde/2214320", "https://www.etuovi.com/kohde/2214733"]
_g_test_addresses = ["Tampere", "Helsinki"]

class TurboTestCase(unittest.TestCase):
    def setUp(self):
        if os.path.exists(_g_jsonfile):
            os.unlink(_g_jsonfile)
    def tearDown(self):
        pass
    def testAddAptAndPrint(self):
        apt = EtuoviApt(_g_test_urls[0])
        print(apt)

    def testGetDistance(self):
        map_helper.get_distance("Seattle", "Los Angeles", "transit")
        car = map_helper.get_distance("Seattle", "Los Angeles")
        pprint.pprint(car)
        assert int(car[2]) > 1700000 and int(car[2]) < 1900000

    def testSaveAndLoad(self):
        def checkFile(apt):
            assert os.path.exists(_g_jsonfile), "File not found! {}".format(_g_jsonfile)
            with open(_g_jsonfile, "r", encoding="utf-8") as fp:
                file_list = json.load(fp)
            
            found = True
            for obj in file_list:
                if obj["url"] == apt.url:
                    found = True
                    assert apt.address == obj["address"], \
                        "Address incorrect! Got {}, expected {}".format(apt.address, obj["address"])
            assert found, "Apartment missing from json file! ({})\n{}".format(apt.address, file_list)
        apt0 = EtuoviApt(_g_test_urls[0], json_file=_g_jsonfile)
        checkFile(apt0)
        apt1 = EtuoviApt(_g_test_urls[1], json_file=_g_jsonfile)
        checkFile(apt1)
        #pprint.pprint(file_dict)

        #Now, load the same url as with apt0. The update time should be same if loading works.
        apt2 = EtuoviApt(_g_test_urls[0], _g_jsonfile)
        assert apt2.last_updated == apt0.last_updated, \
            "Apt load() failed (timestamp has changed) " \
                + str(apt2.last_updated) + " != " + str(apt0.last_updated)

    def testCustomProperties(self):
        """Custom properties can be added and printed."""
        apt = EtuoviApt(_g_test_urls[0])
        value = "Some Value!"
        setattr(apt, "some_custom_property", value)
        assert apt.some_custom_property == value, "Custom property not set" #pylint: disable=E1101
        assert value in str(apt), "Custom property is not in object string representation."
        print(apt)

    def testGetGeocode(self):
        print(map_helper.get_coords(_g_test_addresses[0]))