# Copyright (C) 2004 Anthony Baxter
# Copyright (C) 2004 Jamey Hicks
"""Tests for SDP.

You can run this with command-line:

  $ trial shtoom.test.test_sdp
"""

from twisted.trial import unittest


class SDPTests(unittest.TestCase):

    def testOLDSimpleSDP(self):
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

    def testSDPCreation(self):
        from shtoom.sdp import SDP, MediaDescription
        from shtoom.rtp.formats import PT_PCMU, PT_SPEEX, PT_NTE, PT_CN
        ae = self.assertEquals

        s = SDP()
        md = MediaDescription()
        s.addMediaDescription(md)
        s.setServerIP('127.0.0.1')
        md.setServerIP('127.0.0.1')
        md.setLocalPort(45678)
        md.addRtpMap(PT_PCMU)
        md.addRtpMap(PT_SPEEX)
        md.addRtpMap(PT_CN)
        md.addRtpMap(PT_NTE)
        pts = [ x[1] for x in md.rtpmap.values() ]
        ae(pts, [PT_PCMU, PT_SPEEX, PT_CN, PT_NTE])



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

    def test_multipart_crack(self):
        # cisco creates multipart/mixed messages. I shit you not.
        from twisted.protocols import sip as tpsip
        from shtoom.sip import buildSDP
        ae = self.assertEquals

        l = []
        parser = tpsip.MessagesParser(l.append)
        parser.dataReceived(cisco_multipart_crack)
        parser.dataDone()
        ae(len(l), 1)
        message = l.pop()

        sdp = buildSDP(message)
        # some very basic testing
        rtpmap =  sdp.getMediaDescription('audio').rtpmap
        k = rtpmap.keys() ; k.sort()
        ae(k, [0,13])





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

cisco_multipart_crack = """SIP/2.0 200 OK
Via: SIP/2.0/UDP 192.168.41.57:5067;rport
From: sip:defaultconf@conference.shtoom.net;tag=0260015c
To: sip:00100661396747015@gw2.off.ekorp.com;tag=7B9DD228-940        
Date: Fri, 04 Nov 2005 05:20:22 GMT
Call-ID: 401950999@192.168.41.57
Server: Cisco-SIPGateway/IOS-12.x        
CSeq: 3784 INVITE
Allow: INVITE, OPTIONS, BYE, CANCEL, ACK, PRACK, COMET, REFER, SUBSCRIBE, NOTIFY, INFO
Allow-Events: telephone-event
Contact: <sip:00100661396747015@192.168.41.250:5060>
MIME-Version: 1.0
Content-Type: multipart/mixed;boundary=uniqueBoundary
Content-Length: 405

--uniqueBoundary
Content-Type: application/sdp

v=0
o=CiscoSystemsSIP-GW-UserAgent 9364 4252 IN IP4 192.168.41.250
s=SIP Call
c=IN IP4 192.168.41.250
t=0 0
m=audio 18524 RTP/AVP 0 13
c=IN IP4 192.168.41.250
a=rtpmap:0 PCMU/8000
a=rtpmap:13 CN/8000
--uniqueBoundary
Content-Type: application/gtd
Content-Disposition: signal;handling=optional

ANM,
PRN,isdn*,,NET5*,

--uniqueBoundary--
""".replace("\n", "\r\n")


