
from twisted.trial import unittest


class RTCPdecodeCase(unittest.TestCase):

    def testRoundtripBYE(self):
        testpacket = '\x81\xcb\x00\x01\x03\xe2)\xfa'
        from shtoom.rtp.rtcp import RTCPCompound
        R = RTCPCompound(testpacket)
        ae = self.assertEqual
        ae(len(R),1)
        sdes = R[0]
        ae(sdes.getPT(), 'BYE')
        # Check there was nothing left over
        ae(sdes._body, '')
        enc = R.encode()
        ae(enc, testpacket)

    def testByeWithReason(self):
        from shtoom.rtp.rtcp import RTCPPacket, RTCPCompound
        p = RTCPPacket(pt='BYE', contents=((1000001, 10000002), 'just because'))
        out = p.encode()
        ae = self.assertEqual
        ae(0, len(out)%4)
        ae(out, '\x82\xcb\x00\x06\x00\x0fBA\x00\x98\x96\x82\x0cjust because\x00\x00\x00')
        R = RTCPCompound(out)
        ae(len(R), 1)
        bye = R[0]
        ae(bye.getPT(), 'BYE')
        ae(bye.getContents(), [[1000001, 10000002], 'just because'])

    def testSDESdecode(self):
        testpacket = '\x81\xca\x00\x07\x03\xe2)\xfa\x01\x140.0.0@192.168.41.250\x00\x00'
        from shtoom.rtp.rtcp import RTCPCompound

        R = RTCPCompound(testpacket)
        ae = self.assertEqual
        ae(len(R),1)
        sdes = R[0]
        ae(sdes.getPT(), 'SDES')
        # Check there was nothing left over
        ae(sdes._body, '')
        ae(sdes.encode(), testpacket)

    def testCompoundRTCP(self):
        testpacket = '\x81\xc9\x00\x07\x03\xe2)\xfa\xb5\x96\x9d\xdd\x06\x00\x00\x18\x00\x00\xdd8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x81\xca\x00\x07\x03\xe2)\xfa\x01\x140.0.0@192.168.41.250\x00\x00\x81\xcb\x00\x01\x03\xe2)\xfa'
        from shtoom.rtp.rtcp import RTCPCompound
        R = RTCPCompound(testpacket)
        ae = self.assertEqual
        ae(len(R),3)
        rr, sdes, bye = R
        ae(rr.getPT(), 'RR')
        ae(sdes.getPT(), 'SDES')
        ae(bye.getPT(), 'BYE')
        # Check there was nothing left over
        for r in R:
            ae(r._body, '')
        ae(repr(R), '<RTCP Packet: (RR, SDES, BYE)>')

    def FAILINGtestCompoundRTCP2(self):
        testpacket = '\x81\xc8\x00\x0c\x1d%)\xfa\xc4E\xd4\x88\x97\xffU\x01\x00\x00\x00\x00\x00\x00\x00\xce\x00\x00\x80\xc0\xe1*c\x96\x00\x00\x00\x18\x00\x01\x03\xf2\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x81\xca\x00\x14\x1d%)\xfa\x01\x140.0.0@192.168.41.250\x02\x17Cisco IOS, VoIP Gateway\x06\x17Cisco IOS, VoIP Gateway\x00\x00\x00\x00'
        from shtoom.rtp.rtcp import RTCPCompound
        R = RTCPCompound(testpacket)
        ae = self.assertEqual
        ae(len(R),2)
        for r in R:
            ae(r._body, '')

        """
        RTCP: <RTCP SR [488974842L, {'ntpTS': 14142943887957644545L, 'packets': 206L, 'octets': 32960L, 'rtpTS': 0L}, [{'ssrc': 488974842L, 'jitter': 0L, 'fraclost': 0.765625, 'packlost': 4576392L, 'dlsr': 32960L, 'lsr': 206L, 'highest': 2550093057L}]]  '\xe1*c\x96\x00\x00\x00\x18\x00\x01\x03\xf2\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00'>
        RTCP: <RTCP SDES [(488974842L, [('CNAME', '0.0.0@192.168.41.250'), ('NAME', 'Cisco IOS, VoIP Gateway'), ('TOOL', 'Cisco IOS, VoIP Gateway')])]  '\x00'>
        """

        """
        testpacket = '\x81\xc8\x00\x0c\x1d%)\xfa\xc4E\xd4\x85\x1a\xcd\xdb\x02\x00\x00\x00\x00\x00\x00\x007\x00\x00"`\xe1*c\x96\x01\x00\x00\x18\x00\x01\x03D\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x81\xca\x00\x14\x1d%)\xfa\x01\x140.0.0@192.168.41.250\x02\x17Cisco IOS, VoIP Gateway\x06\x17Cisco IOS, VoIP Gateway\x00\x00\x00\x00'
        RTCP: <RTCP SR [488974842L, {'ntpTS': 14142943872972348162L, 'packets': 55L, 'octets': 8800L, 'rtpTS': 0L}, [{'ssrc': 488974842L, 'jitter': 0L, 'fraclost': 0.765625, 'packlost': 4576389L, 'dlsr': 8800L, 'lsr': 55L, 'highest': 449698562L}]]  '\xe1*c\x96\x01\x00\x00\x18\x00\x01\x03D\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00'>
        RTCP: <RTCP SDES [(488974842L, [('CNAME', '0.0.0@192.168.41.250'), ('NAME', 'Cisco IOS, VoIP Gateway'), ('TOOL', 'Cisco IOS, VoIP Gateway')])]  '\x00'>
        """

"""



'\x81\xc8\x00\x0c\x1d%)\xfa\xc4E\xd4\x88\x97\xffU\x01\x00\x00\x00\x00\x00\x00\x00\xce\x00\x00\x80\xc0\xe1*c\x96\x00\x00\x00\x18\x00\x0
1\x03\xf2\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x81\xca\x00\x14\x1d%)\xfa\x01\x140.0.0@192.168.41.250\x02\x17Cisco IOS, VoIP
 Gateway\x06\x17Cisco IOS, VoIP Gateway\x00\x00\x00\x00'
RTCP: <RTCP SR [488974842L, {'ntpTS': 14142943887957644545L, 'packets': 206L, 'octets': 32960L, 'rtpTS': 0L}, [{'ssrc': 488974842L, 'j
itter': 0L, 'fraclost': 0.765625, 'packlost': 4576392L, 'dlsr': 32960L, 'lsr': 206L, 'highest': 2550093057L}]]  '\xe1*c\x96\x00\x00\x0
0\x18\x00\x01\x03\xf2\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00'>
RTCP: <RTCP SDES [(488974842L, [('CNAME', '0.0.0@192.168.41.250'), ('NAME', 'Cisco IOS, VoIP Gateway'), ('TOOL', 'Cisco IOS, VoIP Gate
way')])]  '\x00'>
received RTCP from ('192.168.41.250', 18735) (136 bytes):
    81c8000c 1d2529fa
    c445d48f 75f814be
    00000000 000001fc
    00013d80 e12a6396
    00000018 0001054a
    00000200 00000000
    00000000 81ca0014
    1d2529fa 0114302e
    302e3040 3139322e
    3136382e 34312e32
    35300217 43697363
    6f20494f 532c2056
    6f495020 47617465
    77617906 17436973
    636f2049 4f532c20
    566f4950 20476174
    65776179 00000000
    00000000 00000000

'\x81\xc8\x00\x0c\x1d%)\xfa\xc4E\xd4\x8fu\xf8\x14\xbe\x00\x00\x00\x00\x00\x00\x01\xfc\x00\x01=\x80\xe1*c\x96\x00\x00\x00\x18\x00\x01\x
05J\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x81\xca\x00\x14\x1d%)\xfa\x01\x140.0.0@192.168.41.250\x02\x17Cisco IOS, VoIP Gatew
ay\x06\x17Cisco IOS, VoIP Gateway\x00\x00\x00\x00'
RTCP: <RTCP SR [488974842L, {'ntpTS': 14142943917451515070L, 'packets': 508L, 'octets': 81280L, 'rtpTS': 0L}, [{'ssrc': 488974842L, 'j
itter': 0L, 'fraclost': 0.765625, 'packlost': 4576399L, 'dlsr': 81280L, 'lsr': 508L, 'highest': 1979192510L}]]  '\xe1*c\x96\x00\x00\x0
0\x18\x00\x01\x05J\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00'>
RTCP: <RTCP SDES [(488974842L, [('CNAME', '0.0.0@192.168.41.250'), ('NAME', 'Cisco IOS, VoIP Gateway'), ('TOOL', 'Cisco IOS, VoIP Gate
way')])]  '\x00'>
received RTCP from ('192.168.41.250', 18735) (136 bytes):
    81c8000c 1d2529fa
    c445d494 5be21dde
    00000000 000002d4
    0001c480 e12a6396
    00000018 0001063f
    00000200 00000000
    00000000 81ca0014
    1d2529fa 0114302e
    302e3040 3139322e
    3136382e 34312e32
    35300217 43697363
    6f20494f 532c2056
    6f495020 47617465
    77617906 17436973
    636f2049 4f532c20
    566f4950 20476174
    65776179 00000000
    00000000 00000000

'\x81\xc8\x00\x0c\x1d%)\xfa\xc4E\xd4\x94[\xe2\x1d\xde\x00\x00\x00\x00\x00\x00\x02\xd4\x00\x01\xc4\x80\xe1*c\x96\x00\x00\x00\x18\x00\x0
1\x06?\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x81\xca\x00\x14\x1d%)\xfa\x01\x140.0.0@192.168.41.250\x02\x17Cisco IOS, VoIP Ga
teway\x06\x17Cisco IOS, VoIP Gateway\x00\x00\x00\x00'
RTCP: <RTCP SR [488974842L, {'ntpTS': 14142943938488704478L, 'packets': 724L, 'octets': 115840L, 'rtpTS': 0L}, [{'ssrc': 488974842L, '
jitter': 0L, 'fraclost': 0.765625, 'packlost': 4576404L, 'dlsr': 115840L, 'lsr': 724L, 'highest': 1541545438L}]]  '\xe1*c\x96\x00\x00\
x00\x18\x00\x01\x06?\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00'>
RTCP: <RTCP SDES [(488974842L, [('CNAME', '0.0.0@192.168.41.250'), ('NAME', 'Cisco IOS, VoIP Gateway'), ('TOOL', 'Cisco IOS, VoIP Gate
way')])]  '\x00'>

"""
