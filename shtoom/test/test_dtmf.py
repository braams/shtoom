# Copyright (C) 2004 Anthony Baxter
"""Tests for shtoom.doug.dtmfdetect
"""

from twisted.trial import unittest
def getDTMFAudioFile():
    from twisted.python.util import sibpath
    return sibpath(__file__, 'dtmftestfile.raw')

class DTMFDetectTest(unittest.TestCase):
    def setUp(self):
        try:
            import numarray
        except:
            raise unittest.SkipTest('numarray needed for dtmf detection')

    def test_dtmfdetection_canned(self):
        from shtoom.doug.dtmf import DtmfDetector
        fp = open(getDTMFAudioFile(),'rb')
        dtmf = DtmfDetector()
        seen = []
        cur = None
        while True:
            data = fp.read(640)
            if len(data) != 640: 
                break
            digit = dtmf.detect(data)
            if digit != cur:
                seen.append(digit)
                cur = digit
        self.assertEquals(seen, ['', '3', '', '1', '', '4', '', '1', '', '#'])

    def test_dtmfdetect_generated(self):
        from shtoom.doug import dtmf
        detect = dtmf.DtmfDetector()
        for k in dtmf.dtmf2freq.keys():
            s = dtmf.dtmfGenerator(k, 320)
            digit = detect.detect(s)
            self.assertEquals(k, digit)

    def test_dtmfdetect_speex(self):
        # Test DTMF after the mangling of speex
        import shtoom.avail.codecs
        if shtoom.avail.codecs.speex is None:
            raise unittest.SkipTest('needs speex support')
        from shtoom.audio.converters import SpeexCodec
        codec = SpeexCodec()
        self._test_with_codec(codec)

    def test_dtmfdetect_gsm(self):
        #raise unittest.SkipTest('gsm codec breaks dtmf detection :-(')
        # Test DTMF after the mangling of GSM
        import shtoom.avail.codecs
        if shtoom.avail.codecs.gsm is None:
            raise unittest.SkipTest('needs gsm support')
        from shtoom.audio.converters import GSMCodec
        codec = GSMCodec()
        self._test_with_codec(codec)

    def _test_with_codec(self, codec):
        from shtoom.doug import dtmf
        detect = dtmf.DtmfDetector()
        for k in dtmf.dtmf2freq.keys():
            s = dtmf.dtmfGenerator(k, 320)
            s1, s2 = s[:320], s[320:]
            codec.decode(codec.encode(s1))
            codec.decode(codec.encode(s2))
            s1 = codec.decode(codec.encode(s1))
            s2 = codec.decode(codec.encode(s2))
            s = s1+s2
            digit = detect.detect(s)
            self.assertEquals(k, digit)
            silence = '\0'*320
            codec.decode(codec.encode(silence))
