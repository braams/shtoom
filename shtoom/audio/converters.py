# Copyright (C) 2004 Anthony Baxter
import audioop

class NullConv:
    def __init__(self, device):
        print "audio: __init__"
        self._d = device
    def getDevice(self):
        return self._d
    def setDevice(self, d):
        self._d = d
    def getFormats(self):
        return self._d.getFormats()
    def selectFormat(self, format):
        return self._d.selectFormat(format)
    def read(self):
        return self._d.read()
    def write(self, data):
        return self._d.write(data)
    def close(self):
        print "audio: close"
        return self._d.close()
    def reopen(self):
        print "audio: reopen"
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

from shtoom.audio import FMT_PCMU, FMT_GSM, FMT_SPEEX, FMT_DVI4, FMT_RAW

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
        print "audio: listFormats"
        if gsm is not None:
            return [FMT_GSM, FMT_PCMU, FMT_RAW,]
        else:
            return [FMT_PCMU, FMT_RAW,]

    def selectFormat(self, fmt):
        print "audio: selectFormats"
        if not fmt in self.listFormats():
            raise ValueError, "unknown format"
        else:
            self._fmt = fmt

    def read(self, format=None):
        if format is None:
            format = self._fmt
        if format == FMT_PCMU:
            return audioop.lin2ulaw(self._d.read(), 2)
        elif format == FMT_RAW:
            return self._d.read()
        elif format == FMT_GSM:
            if self._gsmencoder:
                indata = self._d.read()
                if len(indata) != 320:
                    print "GSM: got short read len = %s"%len(indata)
                    return None
                else:
                    outdata = self._gsmencoder.encode(indata)
                    return outdata
            else:
                print "No GSM available"
        else:
            raise ValueError, "Unknown format %s"%(format)

    def write(self, data, format):
        print "audio: write"
        if format == FMT_PCMU:
            return self._d.write(audioop.ulaw2lin(data, 2))
        elif format == FMT_RAW:
            return self._d.write(data)
        elif format == FMT_GSM:
            if self._gsmdecoder:
                if len(data) != 33:
                    print "GSM: warning: %d bytes of data, not 33"%len(data)
                    return 0
                else:
                    decdata = self._gsmdecoder.decode(data)
                    self._d.write(decdata)
                    return 33
            else:
                print "No GSM available"
        else:
            raise ValueError, "Unknown format %s"%(format)

class DougConverter:
    " yeah, yeah, refactor me "
    def __init__(self, *args, **kwargs):
        self._fmt = FMT_PCMU
        if gsm is not None:
            self._gsmencoder = gsm.gsm(gsm.LITTLE)
            self._gsmdecoder = gsm.gsm(gsm.LITTLE)
        else:
            self._gsmencoder = self._gsmdecoder = None

    def listFormats(self):
        if gsm is not None:
            return [FMT_GSM, FMT_PCMU, FMT_RAW,]
        else:
            return [FMT_PCMU, FMT_RAW,]

    def selectFormat(self, fmt):
        if not fmt in self.listFormats():
            raise ValueError, "unknown format"
        else:
            self._fmt = fmt

    def getFormat(self):
        return self._fmt

    def convertOutbound(self, indata):
        format = self._fmt
        if format == FMT_PCMU:
            return audioop.lin2ulaw(indata, 2)
        elif format == FMT_RAW:
            return indata
        elif format == FMT_GSM:
            if self._gsmencoder:
                if len(indata) != 320:
                    print "GSM: got short read len = %s"%len(indata)
                    return None
                else:
                    outdata = self._gsmencoder.encode(indata)
                    return outdata
            else:
                print "No GSM available"
        else:
            raise ValueError, "Unknown format %s"%(format)

    def convertInbound(self, format, indata):
        if format == FMT_PCMU:
            return audioop.ulaw2lin(indata, 2)
        elif format == FMT_RAW:
            return indata
        elif format == FMT_GSM:
            if self._gsmdecoder:
                if len(indata) != 33:
                    print "GSM: warning: %d bytes of data, not 33"%len(indata)
                    return ''
                else:
                    decdata = self._gsmdecoder.decode(indata)
                    return decdata
            else:
                print "No GSM available"
        else:
            raise ValueError, "Unknown format %s"%(format)

