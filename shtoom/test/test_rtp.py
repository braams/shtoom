# Copyright (C) 2004 Anthony Baxter
"""Tests for shtoom.rtp
"""

from twisted.trial import unittest


class TestRTP(unittest.TestCase):
    def testNTEencoding(self):
        from shtoom.rtp import NTE
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

