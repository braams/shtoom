import glob, os
from twisted.protocols.sip import MessagesParser as MP

from twisted.trial import unittest

testdir = os.path.dirname(__file__)

class SIPParser(unittest.TestCase):

    def test_parse1_msg(self):
        print os.getcwd()
        sip = open(os.path.join(testdir, 'test1.txt')).read()
        mp = MP(self.cb_parse1)
        m = mp.dataReceived(sip)
        mp.dataDone()
        print "DONE"

    def cb_parse1(self, m):
        print "CALLBACK"
        print m.method, m.headers['call-id']

    def cb_parseXX(self, m):
        pass

    def test_parse2_msg(self):
        sip = open(os.path.join(testdir, 'test2.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse3_msg(self):
        sip = open(os.path.join(testdir, 'test3.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse4_msg(self):
        sip = open(os.path.join(testdir, 'test4.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse5_msg(self):
        sip = open(os.path.join(testdir, 'test5.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse6_msg(self):
        sip = open(os.path.join(testdir, 'test6.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse7_msg(self):
        sip = open(os.path.join(testdir, 'test7.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse8_msg(self):
        sip = open(os.path.join(testdir, 'test8.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse9_msg(self):
        sip = open(os.path.join(testdir, 'test9.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse10_msg(self):
        sip = open(os.path.join(testdir, 'test10.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse11_msg(self):
        sip = open(os.path.join(testdir, 'test11.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse12_msg(self):
        sip = open(os.path.join(testdir, 'test12.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse13_msg(self):
        sip = open(os.path.join(testdir, 'test13.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse14_msg(self):
        sip = open(os.path.join(testdir, 'test14.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse15_msg(self):
        sip = open(os.path.join(testdir, 'test15.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse16_msg(self):
        sip = open(os.path.join(testdir, 'test16.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse17_msg(self):
        sip = open(os.path.join(testdir, 'test17.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse18_msg(self):
        sip = open(os.path.join(testdir, 'test18.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse19_msg(self):
        sip = open(os.path.join(testdir, 'test19.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse20_msg(self):
        sip = open(os.path.join(testdir, 'test20.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse21_msg(self):
        sip = open(os.path.join(testdir, 'test21.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse22_msg(self):
        sip = open(os.path.join(testdir, 'test22.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse23_msg(self):
        sip = open(os.path.join(testdir, 'test23.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse24_msg(self):
        sip = open(os.path.join(testdir, 'test24.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse25_msg(self):
        sip = open(os.path.join(testdir, 'test25.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse26_msg(self):
        sip = open(os.path.join(testdir, 'test26.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse27_msg(self):
        sip = open(os.path.join(testdir, 'test27.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse28_msg(self):
        sip = open(os.path.join(testdir, 'test28.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse29_msg(self):
        sip = open(os.path.join(testdir, 'test29.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse30_msg(self):
        sip = open(os.path.join(testdir, 'test30.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse31_msg(self):
        sip = open(os.path.join(testdir, 'test31.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse32_msg(self):
        sip = open(os.path.join(testdir, 'test32.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse33_msg(self):
        sip = open(os.path.join(testdir, 'test33.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse34_msg(self):
        sip = open(os.path.join(testdir, 'test34.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse35_msg(self):
        sip = open(os.path.join(testdir, 'test35.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse36_msg(self):
        sip = open(os.path.join(testdir, 'test36.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse37_msg(self):
        sip = open(os.path.join(testdir, 'test37.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse38_msg(self):
        sip = open(os.path.join(testdir, 'test38.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse39_msg(self):
        sip = open(os.path.join(testdir, 'test39.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse40_msg(self):
        sip = open(os.path.join(testdir, 'test40.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse41_msg(self):
        sip = open(os.path.join(testdir, 'test41.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

    def test_parse42_msg(self):
        sip = open(os.path.join(testdir, 'test42.txt')).read()
        mp = MP(self.cb_parseXX)
        m = mp.dataReceived(sip)

