
from twisted.trial import unittest


class RTCPdecodeCase(unittest.TestCase):

    def testSimpleRTCP(self):
        testpacket = '\x81\xca\x00\x07\x03\xe2)\xfa\x01\x140.0.0@192.168.41.250\x00\x00'
        from shtoom.rtcp import RTCPCompound

        R = RTCPCompound(testpacket)
        ae = self.assertEqual
        ae(len(R),1)
        sdes = R[0]
        ae(sdes.getPT(), 'SDES')
        # Check there was nothing left over
        ae(sdes._body, '')

    def testCompoundRTCP(self):
        testpacket = '\x81\xc9\x00\x07\x03\xe2)\xfa\xb5\x96\x9d\xdd\x06\x00\x00\x18\x00\x00\xdd8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x81\xca\x00\x07\x03\xe2)\xfa\x01\x140.0.0@192.168.41.250\x00\x00\x81\xcb\x00\x01\x03\xe2)\xfa'
        from shtoom.rtcp import RTCPCompound

        R = RTCPCompound(testpacket)
        ae = self.assertEqual
        ae(len(R),3)
        rr, sdes, bye = R
        ae(rr.getPT(), 'RR')
        ae(sdes.getPT(), 'SDES')
        ae(bye.getPT(), 'BYE')
        # Check there was nothing left over
        ae(rr._body, '')
        ae(sdes._body, '')
        ae(bye._body, '')

