# Copyright (C) 2003 Anthony Baxter
import audioop

class NullConv:
    def __init__(self, device):
        self._d = device
    def getDevice(self):
        return self._d
    def getFormats(self):
        return self._d.getFormats()
    def selectFormat(self, format):
        return self._d.selectFormat(format)
    def read(self):
        return self._d.read()
    def write(self, data):
        return self._d.write(data)
    def close(self):
        return self._d.close()
    def reopen(self):
        return self._d.reopen()
    def isClosed(self):
        return self._d.isClosed()

class PCM16toULAWConv(NullConv):
    """ Wraps an audio device that returns Linear PCM and turns it into
        G711 ulaw
    """
    def read(self, count=160, conv=audioop.lin2ulaw):
        count = count * 2
        return conv(self._d.read(count), 2)
    def write(self, bytes, conv=audioop.ulaw2lin):
        return self._d.write(conv(bytes,2))


