# Copyright (C) 2004 Anthony Baxter
"""Tests for shtoom.audio.playout
"""

from twisted.trial import unittest
from shtoom.audio.playout import BrainDeadPlayout, Playout, _Playout

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
