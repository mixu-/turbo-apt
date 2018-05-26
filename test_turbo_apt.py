import unittest
import pprint
import os
import json
import turbo_apt

_g_jsonfile = "test.json"
_g_test_urls = ["https://www.etuovi.com/kohde/620468", "https://www.etuovi.com/kohde/9988654"]
class TurboTestCase(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def testAddAptAndPrint(self):
        apt = turbo_apt.EtuoviApt(_g_test_urls[0])
        print(apt)

    #def testGetDistance(self):
    #    turbo_apt.getDistance("Seattle", "Los Angeles", "transit")
    #    car = turbo_apt.getDistance("Seattle", "Los Angeles")
    #    pprint.pprint(car)
    #    assert int(car[2]) > 1700000 and int(car[2]) < 1900000

    def testSaveAndLoad(self):
        def checkFile(apt):
            assert os.path.exists(_g_jsonfile), "File not found! {}".format(_g_jsonfile)
            with open(_g_jsonfile, "r", encoding="utf-8") as fp:
                file_list = json.load(fp)
                pprint.pprint(file_list)
            
            found = True
            for obj in file_list:
                if obj["url"] == apt.url:
                    found = True
                    assert apt.address == obj["address"], \
                        "Address incorrect! Got {}, expected {}".format(apt.address, obj["address"])
            assert found, "Apartment missing from json file! ({})\n{}".format(apt.address, file_list)
        if os.path.exists(_g_jsonfile):
            os.unlink(_g_jsonfile)
        apt0 = turbo_apt.EtuoviApt(_g_test_urls[0], json_file=_g_jsonfile)
        checkFile(apt0)
        apt1 = turbo_apt.EtuoviApt(_g_test_urls[1], json_file=_g_jsonfile)
        checkFile(apt1)
        #pprint.pprint(file_dict)

        #Now, load the same url as with apt0. The update time should be same if loading works.
        apt2 = turbo_apt.EtuoviApt(_g_test_urls[0], _g_jsonfile)
        assert apt2.last_updated == apt0.last_updated, \
            "Apt load() failed (timestamp has changed) " \
                + str(apt2.last_updated) + " != " + str(apt0.last_updated)