# Copyright (C) 2004 Anthony Baxter
# Copyright (C) 2004 Jamey Hicks
"""Tests for SDP.

You can run this with command-line:

  $ trial shtoom.test.test_sdp
"""

from twisted.trial import unittest


class SDPTests(unittest.TestCase):

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

    def testParseShowSDP(self):
        from shtoom.sdp import SDP
        ae = self.assertEqual
        sdp1 = SDP(sdptext1)
        audio1 = sdp1.getMediaDescription('audio')
        ae(audio1.rtpmap.keys(), [0,3])
        video1 = sdp1.getMediaDescription('video')
        ae(video1.rtpmap.keys(), [31])
        self.assertEquals(sdp1.show(), sdptext1)

    def testIntersectSDP(self):
        from shtoom.sdp import SDP
        ae = self.assertEquals
        sdp1 = SDP(sdptext1)
        ae(sdp1.show(), sdptext1)
        sdp2 = SDP(sdptext2)
        sdp1.intersect(sdp2)
        sdp3 = SDP(sdptext3)
        #ae(sdp1.show(), sdp3.show())
        audio1 = sdp1.getMediaDescription('audio')
        audio3 = sdp3.getMediaDescription('audio')
        ae(audio1.formats, audio3.formats)
        ae(audio1.rtpmap.keys(), [3,])
    
    def testComplexIntersectSDP(self):
        from shtoom.sdp import SDP
        from shtoom.rtp.formats import PT_SPEEX, PT_SPEEX_16K, PT_GSM, PT_PCMU
        sdp4 = SDP(sdptext4)
        ae = self.assertEquals
        ae(sdp4.show(), sdptext4)
        rtpmap = sdp4.getMediaDescription('audio').rtpmap
        ae(rtpmap.keys(), [3, 101])
        sdp5 = SDP(sdptext5)
        rtpmap = sdp5.getMediaDescription('audio').rtpmap
        ae(rtpmap.keys(), [0, 3, 101, 102])
        ae(sdp5.show(), sdptext5)
        sdp4.intersect(sdp5)
        rtpmap = sdp4.getMediaDescription('audio').rtpmap
        ae(rtpmap.keys(), [3, 102])
        sdp6 = SDP(sdptext6)
        rtpmap = sdp6.getMediaDescription('audio').rtpmap
        ae(rtpmap.keys(), [3, 101, 102])
        sdp7 = SDP(sdptext7)
        rtpmap = sdp7.getMediaDescription('audio').rtpmap
        ae(rtpmap.keys(), [0, 3, 101, 102])
        sdp6.intersect(sdp7)
        rtpmap = sdp6.getMediaDescription('audio').rtpmap
        ae(rtpmap.keys(), [3, 101, 102])
        ae(rtpmap[3][1], PT_GSM)
        ae(rtpmap[101][1], PT_SPEEX)
        ae(rtpmap[102][1], PT_SPEEX_16K)



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
a=rtpmap:31 H261/90000/1\r
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
m=audio 49170 RTP/AVP 3\r
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
m=audio 49170 RTP/AVP 3\r
a=rtpmap:3 GSM/8000\r
m=video 51372 RTP/AVP 31\r
"""

sdptext4 = """v=0\r
o=mhandley 2890844526 2890842807 IN IP4 126.16.64.4\r
s=SDP Seminar\r
i=A Seminar on the session description protocol\r
u=http://www.cs.ucl.ac.uk/staff/M.Handley/sdp.03.ps\r
e=mjh@isi.edu (Mark Handley)\r
c=IN IP4 224.2.17.12/127\r
t=2873397496 2873404696\r
a=recvonly\r
m=audio 49170 RTP/AVP 3 101\r
a=rtpmap:3 GSM/8000\r
a=rtpmap:101 speex/8000\r
m=video 51372 RTP/AVP 31\r
a=rtpmap:31 H261/90000/1\r
"""

sdptext5 = """v=0\r
o=mhandley 2890844526 2890842807 IN IP4 126.16.64.4\r
s=SDP Seminar\r
i=A Seminar on the session description protocol\r
u=http://www.cs.ucl.ac.uk/staff/M.Handley/sdp.03.ps\r
e=mjh@isi.edu (Mark Handley)\r
c=IN IP4 224.2.17.12/127\r
t=2873397496 2873404696\r
a=recvonly\r
m=audio 49170 RTP/AVP 0 3 101 102\r
a=rtpmap:0 PCMU/8000\r
a=rtpmap:3 GSM/8000\r
a=rtpmap:101 telephone-event/8000\r
a=rtpmap:102 speex/8000\r
m=video 51372 RTP/AVP 31\r
a=rtpmap:31 H261/90000/1\r
"""

sdptext6 = """v=0\r
o=mhandley 2890844526 2890842807 IN IP4 126.16.64.4\r
s=SDP Seminar\r
i=A Seminar on the session description protocol\r
u=http://www.cs.ucl.ac.uk/staff/M.Handley/sdp.03.ps\r
e=mjh@isi.edu (Mark Handley)\r
c=IN IP4 224.2.17.12/127\r
t=2873397496 2873404696\r
a=recvonly\r
m=audio 49170 RTP/AVP 3 101 102\r
a=rtpmap:101 speex/16000\r
a=rtpmap:102 speex/8000\r
m=video 51372 RTP/AVP 31\r
"""

sdptext7 = """v=0\r
o=mhandley 2890844526 2890842807 IN IP4 126.16.64.4\r
s=SDP Seminar\r
i=A Seminar on the session description protocol\r
u=http://www.cs.ucl.ac.uk/staff/M.Handley/sdp.03.ps\r
e=mjh@isi.edu (Mark Handley)\r
c=IN IP4 224.2.17.12/127\r
t=2873397496 2873404696\r
a=recvonly\r
m=audio 49170 RTP/AVP 0 3 101 102\r
a=rtpmap:0 PCMU/8000\r
a=rtpmap:101 speex/8000\r
a=rtpmap:102 speex/16000\r
m=video 51372 RTP/AVP 31\r
"""

