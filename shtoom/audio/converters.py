# Copyright (C) 2003 Anthony Baxter
import audioop

class NullConv:
    def __init__(self, device):
        self._d = device
    def read(self, count):
        return self._d.read(count)
    def write(self, bytes):
        return self._d.write(bytes)
    def close(self):
        self._d.close()

class PCM16toULAWConv(NullConv):
    """ Wraps an audio device that returns Linear PCM and turns it into
        G711 ulaw
    """
    def read(self, count, conv=audioop.lin2ulaw):
        count = count * 2
        return conv(self._d.read(count), 2)
    def write(self, bytes, conv=audioop.ulaw2lin):
        return self._d.write(conv(bytes,2))


