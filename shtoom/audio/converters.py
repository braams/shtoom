# Copyright (C) 2004 Anthony Baxter
from shtoom.rtp.formats import PT_PCMU, PT_GSM, PT_SPEEX, PT_DVI4, PT_RAW
from shtoom.rtp.formats import PT_CN, PT_xCN
from shtoom.rtp.packets import RTPPacket
from shtoom.avail import codecs
from shtoom.audio.playout import Playout

from twisted.python import log

try:
    import audioop
except ImportError:
    audioop = None

class NullConv:
    # Should be refactored away
    def __init__(self, device):
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
        print "audio: reopen ..."
        return self._d.reopen()
    def isClosed(self):
        return self._d.isClosed()
    def __repr__(self):
        return '<%s wrapped around %r>'%(self.__class__.__name__, self._d)

def isLittleEndian():
    import struct
    p = struct.pack('H', 1)
    if p == '\x01\x00':
        return True
    elif p == '\x00\x01':
        return False
    else:
        raise ValueError("insane endian-check result %r"%(p))

class _Codec:
    "Base class for codecs"

class GSMCodec(_Codec):
    def __init__(self):
        if isLittleEndian():
            self.enc = codecs.gsm.gsm(gsm.LITTLE)
            self.dec = codecs.gsm.gsm(gsm.LITTLE)
        else:
            self.enc = codecs.gsm.gsm(gsm.BIG)
            self.dec = codecs.gsm.gsm(gsm.BIG)

    def encode(self, bytes):
        if len(bytes) != 320:
            log.msg("GSM: got short read len = %s"%len(indata))
            return None
        return self.enc.encode(bytes)

    def decode(self, bytes):
        if len(bytes) != 33:
            print "GSM: warning: %d bytes of data, not 33"%len(bytes)
            return None
        return self.dec.encode(bytes)

class SpeexCodec:
    "A codec for Speex"
    # XXX completely untested

    def __init__(self):
        self.enc = speex.Encoder(8)
        self.dec = speex.Decoder(8)

    def encode(self, bytes):
        # XXX length validity tests?
        return self.enc.Encode(bytes)

    def decode(self, bytes):
        # XXX length validity tests?
        return self.enc.Decode(bytes)

class MulawCodec(_Codec):
    "A codec for mulaw encoded audio (e.g. G.711U)"

    def encode(self, bytes):
        # XXX Check bytes length
        return audioop.lin2ulaw(bytes, 2)

    def decode(self, bytes):
        # XXX Check bytes length
        return audioop.ulaw2lin(bytes, 2)

class AlawCodec(_Codec):
    "A codec for alaw encoded audio (e.g. G.711A)"

    def encode(self, bytes):
        # XXX Check bytes length?
        return audioop.lin2alaw(bytes, 2)

    def decode(self, bytes):
        # XXX Check bytes length?
        return audioop.alaw2lin(bytes, 2)

class NullCodec(_Codec):
    "A codec that consumes/emits nothing (e.g. for confort noise)"

    def encode(self, bytes):
        return None

    def decode(self, bytes):
        return None

class PassthruCodec(_Codec):
    "A codec that leaves it's input alone"
    encode = decode = lambda self, bytes: bytes

class Codecker:
    def __init__(self):
        self.codecs = {}
        self.codecs[PT_CN] = NullCodec()
        self.codecs[PT_xCN] = NullCodec()
        self.codecs[PT_RAW] = PassthruCodec()
        if codecs.mulaw is not None:
            self.codecs[PT_PCMU] = MulawCodec()
        if codecs.alaw is not None:
            self.codecs[PT_PCMA] = AlawCodec()
        if codecs.gsm is not None:
            self.codecs[PT_GSM] = GSMCodec()
        if codecs.speex is not None: 
            self.codecs[PT_GSM] = SpeexCodec()
        if codecs.dvi4 is not None:
            self.codecs[PT_DVI4] = DVI4Codec()
        if codecs.ilbc is not None:
            self.codecs[PT_ILBC] = ILBCCodec()

    def getDefaultFormat(self):
        return self.format

    def setDefaultFormat(self, format):
        if self.codecs.has_key(format):
            self.format = format
        else:
            raise ValueError("Can't handle codec %r"%format)

    def encode(self, bytes):
        "Accepts audio as bytes, emits an RTPPacket"
        if not bytes:
            return None
        codec = self.codecs.get(self.format)
        if not codec:
            raise ValueError("can't encode format %r"%format)
        encaudio = codec.encode(bytes)
        if not encaudio:
            return None
        return RTPPacket(self.format, encaudio, ts=None)

    def decode(self, packet):
        "Accepts an RTPPacket, emits audio as bytes"
        if not packet.data:
            return None
        codec = self.codecs.get(packet.pt)
        if not codec:
            raise ValueError("can't decode format %r"%format)
        encaudio = codec.decode(packet.data)
        return encaudio

class MediaLayer(NullConv):
    """ The MediaLayer sits between the network and the raw
        audio device. It converts the audio to/from the codec on
        the network to the format used by the lower-level audio
        devices (16 bit signed ints at 8KHz).
    """
    def __init__(self, device, defaultFormat=PT_PCMU, *args, **kwargs):
        self.playout = None
        self.audioLC = None
        self.codecker = Codecker()
        self.codecker.setDefaultFormat(defaultFormat)
        NullConv.__init__(self, device, *args, **kwargs)

    def selectDefaultFormat(self, fmt):
        self.codecker.setDefaultFormat(fmt)

    def getFormat(self):
        return self.codecker.getDefaultFormat()

    def read(self):
        bytes = self._d.read()
        return self.codecker.encode(bytes)

    def write(self, packet):
        if self.playout is None:
            log.msg("write before reopen, discarding")
            return 0
        audio = self.codecker.decode(packet)
        if not audio:
            self.playout.write('', packet)
            return 0
        return self.playout.write(audio, packet)

    def reopen(self):
        from twisted.internet.task import LoopingCall
        if self.playout is not None:
            log.msg("duplicate ACK? playout already started")
            return
        self.playout = Playout()
        print "initialising playout", self.playout
        self.audioLC = LoopingCall(self.playoutAudio)
        self.audioLC.start(0.020)

    def playoutAudio(self):
        au = self.playout.read()
        self._d.write(au)

    def close(self):
        if self.audioLC is not None:
            self.audioLC.stop()
            self.audioLC = None
        self.playout = None

class DougConverter(MediaLayer):
    "Specialised converter for Doug."
    # XXX should be refactored away to just use a Codecker directly
    def __init__(self, defaultFormat=PT_PCMU, *args, **kwargs):
        MediaLayer.__init__(self, defaultFormat=defaultFormat, 
                            *args, **kwargs)
        self.convertOutbound = self.codecker.encode
        self.convertInbound = self.codecker.decode
