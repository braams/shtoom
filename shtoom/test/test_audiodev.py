# Copyright (C) 2004 Anthony Baxter
"""Tests for shtoom.audio.getAudioDevice
"""

from twisted.trial import unittest

from shtoom.rtp.formats import PT_PCMU

class _dummy:
    pass

from shtoom.audio.baseaudio import AudioDevice
class FakeDevice(AudioDevice):
    def __init__(self):
        self.open = False
        self.ops = []
        AudioDevice.__init__(self)
    def openDev(self):
        self.open = True
        self.ops.append('openDev')
    def close(self):
        self.open = False
        self.ops.append('close')
    def reopen(self):
        self.open = True
        self.ops.append('reopen')
    def write(self, bytes):
        self.ops.append('write')
    def set_sink(self, sink):
        pass
    def isOpen(self):
        return self.open

class AudioDevsTest(unittest.TestCase):

    def test_create(self):
        from shtoom.audio import getAudioDevice
        from twisted.internet.task import LoopingCall
        ae = self.assertEquals
        a_ = self.assert_

        dummymod = _dummy()
        dev = FakeDevice()
        def Device(dev=dev):
            return dev
        dummymod.Device = Device
        m = getAudioDevice(dummymod)
        m.close()
        m.selectDefaultFormat([PT_PCMU,])

        ae(m.getDevice(), dev)
        a_(m.playout is None)
        m.close()
        a_(m.playout is None)
        m.reopen()
        m.close()
        a_(m.playout is None)
