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

            
