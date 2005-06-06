import glob, os
from twisted.protocols.sip import MessagesParser as MP

from twisted.trial import unittest
from twisted.internet import reactor

testdir = os.path.dirname(__file__)

class SIPParser(unittest.TestCase):

    def test_parse01_msg(self):
        print os.getcwd()
        sip = open(os.path.join(testdir, 'test1.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse01)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse01(self, m):
        self.parsed = 1
        self.assertEquals(m.method.lower(), 'invite')
        self.assertEquals(m.headers['call-id'], '0ha0isndaksdj@10.1.1.1')

    def test_parse02_msg(self):
        sip = open(os.path.join(testdir, 'test2.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse02)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse02(self, m):
        self.parsed = 1
        self.assertEquals(m.method.lower(), 'invite')
        self.assertEquals(m.headers['require'], ['newfeature1, newfeature2'])
        self.assertEquals(m.headers['proxy-require'], ['newfeature3, newfeature4'])

    def test_parse03_msg(self):
        sip = open(os.path.join(testdir, 'test3.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse03)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse03(self, m):
        self.parsed = 1
        self.assertEquals(m.method.lower(), 'invite')
        self.assertEquals(m.headers['to'], 'isbn:2983792873')
        self.assertEquals(m.headers['from'], 'http://www.cs.columbia.edu')
        self.assertEquals(m.headers['contact'], 'Joe Bob Briggs <urn:ipaddr:122.1.2.3>')

    def test_parse04_msg(self):
        sip = open(os.path.join(testdir, 'test4.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse04)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse04(self, m):
        self.parsed = 1

    def test_parse05_msg(self):
        sip = open(os.path.join(testdir, 'test5.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse05)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse05(self, m):
        self.parsed = 1

    def test_parse06_msg(self):
        sip = open(os.path.join(testdir, 'test6.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse06)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse06(self, m):
        self.parsed = 1

    def test_parse07_msg(self):
        sip = open(os.path.join(testdir, 'test7.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse07)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse07(self, m):
        self.parsed = 1

    def test_parse08_msg(self):
        sip = open(os.path.join(testdir, 'test8.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse08)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse08(self, m):
        self.parsed = 1

    def test_parse09_msg(self):
        sip = open(os.path.join(testdir, 'test9.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse09)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse09(self, m):
        self.parsed = 1

    def test_parse10_msg(self):
        sip = open(os.path.join(testdir, 'test10.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse10)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,0)

    def cb_parse10(self, m):
        self.parsed = 1

    def test_parse11_msg(self):
        sip = open(os.path.join(testdir, 'test11.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse11)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse11(self, m):
        self.parsed = 1

    def test_parse12_msg(self):
        sip = open(os.path.join(testdir, 'test12.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse12)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse12(self, m):
        self.parsed = 1

    def test_parse13_msg(self):
        sip = open(os.path.join(testdir, 'test13.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse13)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse13(self, m):
        self.parsed = 1

    def test_parse14_msg(self):
        sip = open(os.path.join(testdir, 'test14.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse14)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse14(self, m):
        self.parsed = 1

    def test_parse15_msg(self):
        sip = open(os.path.join(testdir, 'test15.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse15)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse15(self, m):
        self.parsed = 1

    def test_parse16_msg(self):
        sip = open(os.path.join(testdir, 'test16.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse16)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse16(self, m):
        self.parsed = 1

    def test_parse17_msg(self):
        sip = open(os.path.join(testdir, 'test17.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse17)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,0)

    def cb_parse17(self, m):
        self.parsed = 1

    def test_parse18_msg(self):
        sip = open(os.path.join(testdir, 'test18.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse18)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse18(self, m):
        self.parsed = 1

    def test_parse19_msg(self):
        sip = open(os.path.join(testdir, 'test19.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse19)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse19(self, m):
        self.parsed = 1

    def test_parse20_msg(self):
        sip = open(os.path.join(testdir, 'test20.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse20)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse20(self, m):
        self.parsed = 1

    def test_parse21_msg(self):
        sip = open(os.path.join(testdir, 'test21.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse21)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,0)

    def cb_parse21(self, m):
        self.parsed = 1

    def test_parse22_msg(self):
        sip = open(os.path.join(testdir, 'test22.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse22)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,0)

    def cb_parse22(self, m):
        self.parsed = 1

    def test_parse23_msg(self):
        sip = open(os.path.join(testdir, 'test23.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse23)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,0)

    def cb_parse23(self, m):
        self.parsed = 1

    def test_parse24_msg(self):
        sip = open(os.path.join(testdir, 'test24.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse24)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse24(self, m):
        self.parsed = 1

    def test_parse25_msg(self):
        sip = open(os.path.join(testdir, 'test25.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse25)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,0)

    def cb_parse25(self, m):
        self.parsed = 1

    def test_parse26_msg(self):
        sip = open(os.path.join(testdir, 'test26.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse26)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse26(self, m):
        self.parsed = 1

    def test_parse27_msg(self):
        sip = open(os.path.join(testdir, 'test27.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse27)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse27(self, m):
        self.parsed = 1

    def test_parse28_msg(self):
        sip = open(os.path.join(testdir, 'test28.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse28)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse28(self, m):
        self.parsed = 1

    def test_parse29_msg(self):
        sip = open(os.path.join(testdir, 'test29.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse29)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse29(self, m):
        self.parsed = 1

    def test_parse30_msg(self):
        sip = open(os.path.join(testdir, 'test30.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse30)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse30(self, m):
        self.parsed = 1

    def test_parse31_msg(self):
        sip = open(os.path.join(testdir, 'test31.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse31)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse31(self, m):
        self.parsed = 1

    def test_parse32_msg(self):
        sip = open(os.path.join(testdir, 'test32.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse32)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse32(self, m):
        self.parsed = 1

    def test_parse33_msg(self):
        sip = open(os.path.join(testdir, 'test33.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse33)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse33(self, m):
        self.parsed = 1

    def test_parse34_msg(self):
        sip = open(os.path.join(testdir, 'test34.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse34)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse34(self, m):
        self.parsed = 1

    def test_parse35_msg(self):
        sip = open(os.path.join(testdir, 'test35.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse35)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,0)

    def cb_parse35(self, m):
        self.parsed = 1

    def test_parse36_msg(self):
        sip = open(os.path.join(testdir, 'test36.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse36)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse36(self, m):
        self.parsed = 1

    def test_parse37_msg(self):
        sip = open(os.path.join(testdir, 'test37.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse37)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse37(self, m):
        self.parsed = 1

    def test_parse38_msg(self):
        sip = open(os.path.join(testdir, 'test38.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse38)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse38(self, m):
        self.parsed = 1

    def test_parse39_msg(self):
        sip = open(os.path.join(testdir, 'test39.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse39)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse39(self, m):
        self.parsed = 1

    def test_parse40_msg(self):
        sip = open(os.path.join(testdir, 'test40.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse40)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,1)

    def cb_parse40(self, m):
        self.parsed = 1

    def test_parse41_msg(self):
        sip = open(os.path.join(testdir, 'test41.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse41)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,0)

    def cb_parse41(self, m):
        self.parsed = 1

    def test_parse42_msg(self):
        sip = open(os.path.join(testdir, 'test42.txt')).read().replace('\n','\r\n')
        self.parsed = 0
        mp = MP(self.cb_parse42)
        m = mp.dataReceived(sip)
        mp.dataDone()
        self.assertEquals(self.parsed,0)

    def cb_parse42(self, m):
        self.parsed = 1
