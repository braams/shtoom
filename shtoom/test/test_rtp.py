# Copyright (C) 2004 Anthony Baxter
"""Tests for shtoom.rtp.protocol
"""

from twisted.trial import unittest


class TestRTP(unittest.TestCase):
    def testNTEencoding(self):
        from shtoom.rtp.packets import NTE
        ae = self.assertEquals
        nte = NTE('0', 1000)
        ae(nte.isDone(), False)
        ae(nte.getPayload(1000), '\x00\n\x00\x00')
        ae(nte.getPayload(1001), '\x00\n\x00\x01')
        ae(nte.getPayload(1002), '\x00\n\x00\x02')
        ae(nte.getPayload(1003), None)
        ae(nte.isDone(), False)
        nte.end()
        ae(nte.isDone(), False)
        ae(nte.getPayload(1004), '\x00\x8a\x00\x04')
        ae(nte.isDone(), True)
        ae(nte.getPayload(1004), None)
        ae(nte.isDone(), True)
        for key, payload in ( ( '1', chr(1) ),
                              ( '4', chr(4) ),
                              ( '*', chr(10) ),
                              ( '#', chr(11) ),
                              ( 'A', chr(12) ),
                              ( 'D', chr(15) ),
                              ( 'flash', chr(16) ),
                             ):
            nte = NTE(key, 1000000)
            ae(nte.getKey(), key)
            ae(nte.getPayload(1000258), payload+'\n\x01\x02')

    def testRTPDict(self):
        from shtoom.rtp.formats import PT_CN, PT_PCMU, PT_SPEEX, PT_SPEEX_16K, PT_NTE
        from shtoom.rtp.formats import RTPDict

        ae = self.assertEquals
        ae(PT_CN, RTPDict[RTPDict[PT_CN]])
        ae(PT_PCMU, RTPDict[RTPDict[PT_PCMU]])
        for pt in PT_SPEEX, PT_SPEEX_16K, PT_CN, PT_PCMU, PT_NTE:
            ae(pt, RTPDict[(pt.name.lower(),pt.clock,pt.params or 1)])

    def testRTPPacketRoundTrip(self):
        from shtoom.rtp.packets import RTPPacket
        from shtoom.rtp.protocol import parse_rtppacket
        from shtoom.rtp.formats import PT_PCMU, PT_SPEEX, PT_GSM, PT_CN
        ae = self.assertEquals

        ts = 12345678
        seq = 12345
        ssrc = 100001
        packets = [
            RTPPacket(ssrc, seq, ts, ''.join([chr(x) for x in range(160)]), 0, ct=PT_PCMU),
            RTPPacket(ssrc, seq, ts, '\0'*33, 1, ct=PT_GSM),
            RTPPacket(ssrc, seq, ts, '\0'*33, 0, ct=PT_GSM),
            RTPPacket(ssrc, seq, ts, chr(127), 0, ct=PT_CN),
            RTPPacket(ssrc, seq, ts, chr(127), 1, ct=PT_CN),
                  ]
        for pack in packets:
            rpack = parse_rtppacket(pack.netbytes())
            ae(pack.header.pt, rpack.header.pt)
            ae(pack.header.marker, rpack.header.marker)
            ae(pack.data, rpack.data)
            ae(rpack.header.seq, seq)
            ae(rpack.header.ts, ts)
            ae(rpack.header.ssrc, ssrc)

    def testSDPGen(self):
        from shtoom.rtp.formats import SDPGenerator, PTMarker
        from shtoom.sdp import SDP
        a_ = self.assert_
        class DummyRTP:
            def getVisibleAddress(self):
                return ('127.0.0.1', 23456)
        rtp = DummyRTP()
        sdp = SDP(SDPGenerator().getSDP(rtp).show())
        rtpmap = sdp.getMediaDescription('audio').rtpmap
        for pt, (entry, ptmarker) in rtpmap.items():
            a_(isinstance(ptmarker, PTMarker))
