# Copyright (C) 2004 Anthony Baxter
# Copyright (C) 2004 Jamey Hicks
"""Tests for new SDP.

You can run this with command-line:

  $ trial shtoom.test.test_new_sdp
"""

from twisted.trial import unittest

sdptext1 = """v=0\r
o=mhandley 2890844526 2890842807 IN IP4 126.16.64.4\r
s=SDP Seminar\r
i=A Seminar on the session description protocol\r
u=http://www.cs.ucl.ac.uk/staff/M.Handley/sdp.03.ps\r
e=mjh@isi.edu (Mark Handley)\r
c=IN IP4 224.2.17.12/127\r
t=2873397496 2873404696\r
a=recvonly\r
m=audio 49170 RTP/AVP 0 3\r
a=rtpmap:0 PCMU/8000\r
a=rtpmap:3 GSM/8000\r
m=video 51372 RTP/AVP 31\r
m=application 32416 udp wb\r
a=orient:portrait\r
"""

sdptext2 = """v=0\r
o=mhandley 2890844526 2890842807 IN IP4 126.16.64.4\r
s=SDP Seminar\r
i=A Seminar on the session description protocol\r
u=http://www.cs.ucl.ac.uk/staff/M.Handley/sdp.03.ps\r
e=mjh@isi.edu (Mark Handley)\r
c=IN IP4 224.2.17.12/127\r
t=2873397496 2873404696\r
a=recvonly\r
m=audio 49170 RTP/AVP 0\r
a=rtpmap:3 GSM/8000\r
m=video 51372 RTP/AVP 31\r
"""

sdptext3 = """v=0\r
o=mhandley 2890844526 2890842807 IN IP4 126.16.64.4\r
s=SDP Seminar\r
i=A Seminar on the session description protocol\r
u=http://www.cs.ucl.ac.uk/staff/M.Handley/sdp.03.ps\r
e=mjh@isi.edu (Mark Handley)\r
c=IN IP4 224.2.17.12/127\r
t=2873397496 2873404696\r
a=recvonly\r
m=audio 49170 RTP/AVP 0 3\r
a=rtpmap:3 GSM/8000\r
m=video 51372 RTP/AVP 31\r
"""

class SDPGeneration(unittest.TestCase):

    def testParseShowSDP(self):
        from shtoom.sdp import SDP
        sdp1 = SDP(sdptext1)
        self.assertEquals(sdp1.show(), sdptext1)

    def testIntersectSDP(self):
        from shtoom.sdp import SDP
        sdp1 = SDP(sdptext1)
        self.assertEquals(sdp1.show(), sdptext1)
        sdp2 = SDP(sdptext2)
        sdp1.intersect(sdp2)
        sdp3 = SDP(sdptext3)
        self.assertEquals(sdp1.show(), sdp3.show())
        
