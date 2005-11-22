# Copyright (C) 2004 Anthony Baxter

# A special audio device. It merely echoes back what you send it.

from converters import MediaLayer
import baseaudio

opened = None

class EchoAudioDevice(baseaudio.AudioDevice):

    def __init__(self):
        self._data = ''
        baseaudio.AudioDevice.__init__(self)

    def _push_up_some_data(self):
        sample, self._data = self._data[-320:], ''
        if self.encoder and self._data:
            self.encoder.handle_audio(self._data)

    def write(self, bytes):
        self._data += bytes

    def _close(self):
        self._data = ''
        try:
            self.LC.stop()
        except AttributeError:
            # workaround for twisted bug
            pass

    def openDev(self):
        from twisted.internet.task import LoopingCall
        self.LC = LoopingCall(self._push_up_some_data)
        self.LC.start(0.020)
        self._data = ''

Device = EchoAudioDevice
