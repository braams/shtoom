# Copyright (C) 2004 Anthony Baxter
"""Tests for shtoom.audio.playout
"""

from twisted.trial import unittest
from shtoom.audio.playout import BrainDeadPlayout, Playout, _Playout
from shtoom.rtp.packets import RTPPacket

class BrainDeadPlayoutTests(unittest.TestCase):

    def test_playout_ctor(self):
        a_ = self.assert_
        b = BrainDeadPlayout()
        a_(isinstance(b, _Playout))
        b = Playout()
        a_(isinstance(b, _Playout))

    def test_braindead(self):
        ae = self.assertEquals
        p = BrainDeadPlayout()
        p.write('1')
        p.write('2')
        ae(p.read(), '1')
        ae(p.read(), '2')
        ae(p.read(), '')
        p.write('3')
        p.write('4')
        p.write('5')
        p.write('6')
        ae(p.read(), '5')
        ae(p.read(), '6')
        ae(p.read(), '')
        p.write('7')
        ae(p.read(), '')
        p.write('8')
        ae(p.read(), '7')
        p.write('9')
        ae(p.read(), '8')
        ae(p.read(), '9')
        ae(p.read(), '')
        p.write('1')
        p.write('')
        ae(p.read(), '1')
        p.write('2')
        ae(p.read(), '')
        ae(p.read(), '2')
        ae(p.read(), '')
        ae(p.read(), '')
        p.write('1')
        ae(p.read(), '')
        p.write('2')
        ae(p.read(), '1')
        p.write('3')
        ae(p.read(), '2')
        p.write('4')
        ae(p.read(), '3')
        ae(p.read(), '4')
        ae(p.read(), '')
        ae(p.read(), '')

    def test_playout_packets(self):
        "Test with RTP Packets"

        ae = self.assertEquals
        for playout in ( BrainDeadPlayout, ): # Add more as I write them

            def _packetgen():
                ts = 0
                while True:
                    yield RTPPacket(data='', pt=None, ts=ts)
                    ts += 160
            p = playout()
            pg = _packetgen()
            p.write('1',pg.next())
            p.write('2',pg.next())
            ae(p.read(), '1')
            ae(p.read(), '2')
            ae(p.read(), '')
            p.write('3',pg.next())
            p.write('4',pg.next())
            p.write('5',pg.next())
            p.write('6',pg.next())
            ae(p.read(), '5')
            ae(p.read(), '6')
            ae(p.read(), '')
            p.write('7',pg.next())
            ae(p.read(), '')
            p.write('8',pg.next())
            ae(p.read(), '7')
            p.write('9',pg.next())
            ae(p.read(), '8')
            ae(p.read(), '9')
            ae(p.read(), '')
            p.write('1',pg.next())
            p.write('',pg.next())
            ae(p.read(), '1')
            p.write('2',pg.next())
            ae(p.read(), '')
            ae(p.read(), '2')
            ae(p.read(), '')
            ae(p.read(), '')
            p.write('1',pg.next())
            ae(p.read(), '')
            p.write('2',pg.next())
            ae(p.read(), '1')
            p.write('3',pg.next())
            ae(p.read(), '2')
            p.write('4',pg.next())
            ae(p.read(), '3')
            ae(p.read(), '4')
            ae(p.read(), '')
            ae(p.read(), '')
