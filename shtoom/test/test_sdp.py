

from unittest import TestCase, TestSuite, main, makeSuite

class SDPGeneration(TestCase):
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
        



def test_suite():
    return TestSuite((
        makeSuite(SDPGeneration),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')

