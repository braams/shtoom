# Copyright (C) 2003 Anthony Baxter
"""Tests for SDP.

You can run this with command-line:

  $ trial shtoom.test.test_sdp
"""

from twisted.trial import unittest


class SDPGeneration(unittest.TestCase):
    
    def testSimpleSDP(self):
        from shtoom.multicast.SDP import SDP, SimpleSDP
        s = SimpleSDP()
        s.setServerIP('10.11.12.13')
        s.setLocalPort(1234)
        s.addRtpMap('PCMU', 8000)
        s.addRtpMap('GSM', 8000)
        sdpin = s.show()
        sdpout = SDP(sdpin)
        ae = self.assertEquals
        ae(sdpout.port, 1234)
        ae(sdpout.ipaddr, '10.11.12.13')
        ae(sdpout.get('a', 'rtpmap'), ['0 PCMU/8000/1', '3 GSM/8000/1'])
        ae(sdpout.formats, [0,3])
        ae(sdpout.media, 'audio')
        ae(sdpout.transport, 'RTP/AVP')
