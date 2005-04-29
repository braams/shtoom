# Copyright (C) 2004 Anthony Baxter

# A special audio device. It merely echoes back what you send it.

from converters import MediaLayer

opened = None

class EchoAudioDevice:
    _closed = True

    def __init__(self):
        self._data = ''

    def _push_up_some_data(self):
        sample, self._data = self._data[-320:], ''
        if self.encoder and data:
            self.encoder.handle_audio(data)

    def write(self, bytes):
        self._data += bytes

    def reopen(self):
        self._closed = False
        self._data = ''

    def close(self):
        if self._closed:
            return
        self._closed = True
        self._data = ''
        try:
            self.LC.stop()
        except AttributeError:
            # workaround for twisted bug
            pass

    def openDev(self):
        self._open = True
        self.LC = LoopingCall(self._push_up_some_data)
        self.LC.start(0.020)

Device = EchoAudioDevice
