# Copyright (C) 2004 Anthony Baxter

# A special audio device. It merely echoes back what you send it.

from converters import MediaLayer

opened = None

class EchoAudio:
    def __init__(self):
        self._data = ''

    def read(self):
        sample, self._data = self._data[-320:], ''
        return sample

    def write(self, bytes):
        self._data += bytes

    def reopen(self):
        self._data = ''

    def close(self):
        self._data = ''

def getEchoAudio():
    return MediaLayer(EchoAudio())
