import unittest
import pprint
import turbo_apt


class TurboTestCase(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def testAddAptAndPrint(self):
        apt = turbo_apt.EtuoviApt("https://www.etuovi.com/kohde/9449326")
        print(apt)

    def testGetDistance(self):
        turbo_apt.getDistance("Seattle", "Los Angeles", "transit")
        car = turbo_apt.getDistance("Seattle", "Los Angeles")
        pprint.pprint(car)
        assert int(car[2]) > 1700000 and int(car[2]) < 1900000
