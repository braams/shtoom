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

try:
    import gsm
except ImportError:
    gsm = None

class PCM16toGSMConv(NullConv):
    def __init__(self, *args, **kwargs):
        if gsm is not None:
            self._encoder = gsm.gsm(gsm.LITTLE)
            self._decoder = gsm.gsm(gsm.LITTLE)
        NullConv.__init__(self, *args, **kwargs)

    def read(self, count=33):
        indata = self._d.read(320)
        encdata = self._encoder.encode(indata)
        return encdata

    def write(self, data):
        if len(data) != 33:
            print "warning: didn't see 33 bytes of data, but %s"%len(data)
        decdata = self._decoder.decode(data)
        self._d.write(decdata)
        return 33

if gsm is None:
    del PCM16toGSMConv

from shtoom.audio import FMT_PCMU, FMT_GSM, FMT_SPEEX, FMT_DVI4

class MultipleConv(NullConv):
    """ Goddam Asterisk """

    def __init__(self, *args, **kwargs):
        self._fmt = FMT_PCMU
        if gsm is not None:
            self._gsmencoder = gsm.gsm(gsm.LITTLE)
            self._gsmdecoder = gsm.gsm(gsm.LITTLE)
        else:
            self._gsmencoder = self._gsmdecoder = None
        NullConv.__init__(self, *args, **kwargs)

    def listFormats(self):
        if gsm is not None:
            return [FMT_PCMU, FMT_GSM]
        else:
            return [FMT_PCMU,]

    def selectFormat(self, fmt):
        if not fmt in self.listFormats:
            raise ValueError, "unknown format"
        else:
            self._fmt = fmt

    def read(self, format=None):
        if format is None:
            format = self._fmt
        if format == FMT_PCMU:
            return audioop.lin2ulaw(self._d.read(320), 2)
        elif format == FMT_GSM:
            if self._gsmencoder:
                indata = self._d.read(320)
                return self._encoder.encode(indata)
            else:
                print "No GSM available"
        else:
            raise ValueError, "Unknown format %s"%(format)

    def write(self, data, format):
        if format == FMT_PCMU:
            return self._d.write(audioop.ulaw2lin(data, 2))
        elif format == FMT_GSM:
            if self._gsmdecoder:
                if len(data) != 33:
                    print "warning: ! 33 bytes of data, but %s"%len(data)
                    decdata = self._decoder.decode(data)
                    self._d.write(decdata)
                    return 33
            else:
                print "No GSM available"
        else:
            raise ValueError, "Unknown format %s"%(format)

