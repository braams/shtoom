# Copyright (C) 2004 Anthony Baxter
"""Tests for shtoom.audio.getAudioDevice
"""

from twisted.trial import unittest

class _dummy:
    pass

from shtoom.audio.baseaudio import AudioDevice
class FakeDevice(AudioDevice):
    def __init__(self):
        self.ops = []
        AudioDevice.__init__(self)
    def openDev(self):
        self.ops.append('openDev')
    def close(self):
        self.ops.append('close')
    def reopen(self):
        self.ops.append('reopen')
    def write(self, bytes):
        self.ops.append('write')
    def read(self):
        self.ops.append('read')

class AudioDevsTest(unittest.TestCase):

    def test_create(self):
        from shtoom.audio import getAudioDevice
        from shtoom.audio.playout import _Playout
        from twisted.internet.task import LoopingCall
        ae = self.assertEquals
        a_ = self.assert_

        dummymod = _dummy()
        dev = FakeDevice()
        def Device(dev=dev):
            return dev
        dummymod.Device = Device
        m = getAudioDevice(dummymod)

        ae(m.getDevice(), dev)
        a_(m.audioLC is None)
        a_(m.playout is None)
        m.close()
        a_(m.audioLC is None)
        a_(m.playout is None)
        m.reopen()
        a_(isinstance(m.playout, _Playout))
        a_(isinstance(m.audioLC, LoopingCall))
        m.close()
        a_(m.audioLC is None)
        a_(m.playout is None)
        ae(dev.ops, ['openDev', 'close', 'reopen', 'write', 'close'])
