# Copyright (C) 2004 Anthony Baxter
import audioop
from shtoom.rtp.formats import PT_PCMU, PT_GSM, PT_SPEEX, PT_DVI4, PT_RAW
from shtoom.rtp.formats import PT_CN, PT_xCN
from shtoom.rtp.packets import RTPPacket

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
    def selectDefaultFormat(self, format):
        return self._d.selectDefaultFormat(format)
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

    def __repr__(self):
        return '<%s wrapped around %r>'%(self.__class__.__name__, self._d)

class PCM16toULAWConv(NullConv):
    """ Wraps an audio device that returns Linear PCM and turns it into
        G711 ulaw
    """
    def read(self, count=160, conv=audioop.lin2ulaw):
        count = count * 2
        return conv(self._d.read(count), 2)
    def write(self, bytes, conv=audioop.ulaw2lin):
        return self._d.write(conv(bytes,2))

from shtoom.avail import gsm

if gsm is not None:
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



class MediaLayer(NullConv):
    """ The MediaLayer sits between the network and the raw
        audio device. It converts the audio to/from the codec on
        the network to the format used by the lower-level audio
        devices (16 bit signed ints at 8KHz).
    """

    def __init__(self, *args, **kwargs):
        self._fmt = PT_PCMU # default format PCMU
        if gsm is not None:
            self._gsmencoder = gsm.gsm(gsm.LITTLE)
            self._gsmdecoder = gsm.gsm(gsm.LITTLE)
        else:
            self._gsmencoder = self._gsmdecoder = None
        NullConv.__init__(self, *args, **kwargs)

    def selectDefaultFormat(self, fmt):
        print "audio: selectDefaultFormats"
        self._fmt = fmt

    def read(self):
        format = self._fmt
        if format == PT_PCMU:
            lin = self._d.read()
            if lin is None: return None
            ret = RTPPacket(format, audioop.lin2ulaw(lin, 2), ts=None)
        elif format == PT_RAW:
            ret = RTPPacket(format, self._d.read(), ts=None)
        elif format == PT_GSM:
            if self._gsmencoder:
                indata = self._d.read()
                if indata is None:
                    ret = None
                elif len(indata) != 320:
                    print "GSM: got short read len = %s"%len(indata)
                    ret = None
                else:
                    outdata = self._gsmencoder.encode(indata)
                    ret = RTPPacket(format, outdata, ts=None)
            else:
                print "No GSM available"
        else:
            raise ValueError, "Unknown format %s"%(format)
        if ret.data is None:
            return None
        return ret

    def write(self, packet):
        #print "audio: write"
        if not packet.data:
            return 0
        data = packet.data
        if packet.pt == PT_PCMU:
            return self._d.write(audioop.ulaw2lin(data, 2))
        elif packet.pt == PT_RAW:
            return self._d.write(data)
        elif packet.pt == PT_GSM:
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
        elif packet.pt in ( PT_CN, PT_xCN ):
            return None
        else:
            raise ValueError, "Unknown format %s"%(packet.pt)

class DougConverter:
    " yeah, yeah, refactor me "
    def __init__(self, *args, **kwargs):
        self._fmt = PT_PCMU
        if gsm is not None:
            self._gsmencoder = gsm.gsm(gsm.LITTLE)
            self._gsmdecoder = gsm.gsm(gsm.LITTLE)
        else:
            self._gsmencoder = self._gsmdecoder = None

    def selectDefaultFormat(self, fmt):
        self._fmt = fmt

    def getFormat(self):
        return self._fmt

    def convertOutbound(self, indata):
        format = self._fmt
        if format == PT_PCMU:
            return RTPPacket(format, audioop.lin2ulaw(indata, 2), ts=None)
        elif format == PT_RAW:
            return RTPPacket(format, indata, ts=None)
        elif format == PT_GSM:
            if self._gsmencoder:
                if len(indata) != 320:
                    print "GSM: got short read len = %s"%len(indata)
                    return None
                else:
                    outdata = self._gsmencoder.encode(indata)
                    return RTPPacket(format, outdata, ts=None)
            else:
                print "No GSM available"
        else:
            raise ValueError, "Unknown format %s"%(format)

    def convertInbound(self, packet):
        if packet.pt == PT_PCMU:
            return audioop.ulaw2lin(indata, 2)
        elif packet.pt == PT_RAW:
            return indata
        elif packet.pt == PT_GSM:
            if self._gsmdecoder:
                if len(indata) != 33:
                    print "GSM: warning: %d bytes of data, not 33"%len(indata)
                    return ''
                else:
                    decdata = self._gsmdecoder.decode(indata)
                    return decdata
            else:
                print "No GSM available"
        elif packet.pt in ( PT_CN, PT_xCN ):
            return None
        else:
            raise ValueError, "Unknown format %s"%(packet.pt)

