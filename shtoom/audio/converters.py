# Copyright (C) 2004 Anthony Baxter
from shtoom.rtp.formats import PT_PCMU, PT_GSM, PT_SPEEX, PT_DVI4, PT_RAW
from shtoom.rtp.formats import PT_PCMA, PT_ILBC
from shtoom.rtp.formats import PT_CN, PT_xCN, AudioPTMarker
from shtoom.rtp.packets import RTPPacket
from shtoom.avail import codecs
from shtoom.audio.playout import Playout
from twisted.python import log
import struct
from shtoom.lwc import Interface, implements

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
        if self._d:
            return self._d.getFormats()
    def selectDefaultFormat(self, format):
        if self._d:
            return self._d.selectDefaultFormat(format)
    def read(self):
        if self._d:
            return self._d.read()
    def write(self, data):
        if self._d:
            return self._d.write(data)
    def close(self):
        if self._d:
            print "audio: close"
            return self._d.close()
    def reopen(self):
        if self._d:
            print "audio: reopen ..."
            return self._d.reopen()
    def isClosed(self):
        if self._d:
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

class IAudioCodec:
    def encode(bytes):
        "encode bytes, a string of audio"
    def decode(bytes):
        "decode bytes, a string of audio"

class _Codec:
    "Base class for codecs"
    implements(IAudioCodec)

class GSMCodec(_Codec):
    def __init__(self):
        if isLittleEndian():
            self.enc = codecs.gsm.gsm(codecs.gsm.LITTLE)
            self.dec = codecs.gsm.gsm(codecs.gsm.LITTLE)
        else:
            self.enc = codecs.gsm.gsm(codecs.gsm.BIG)
            self.dec = codecs.gsm.gsm(codecs.gsm.BIG)

    def encode(self, bytes):
        if len(bytes) != 320:
            log.msg("GSM: short read on encode, %d != 320"%len(bytes), 
                                                            system="codec")
            return None
        return self.enc.encode(bytes)

    def decode(self, bytes):
        if len(bytes) != 33:
            log.msg("GSM: short read on decode, %d !=  33"%len(bytes), 
                                                            system="codec")
            return None
        return self.dec.decode(bytes)

class SpeexCodec(_Codec):
    "A codec for Speex"

    def __init__(self):
        self.enc = codecs.speex.new(8)
        self.dec = codecs.speex.new(8)

    def encode(self, bytes, unpack=struct.unpack):
        if len(bytes) != 320:
            log.msg("speex: short read on encode, %d != 320"%len(bytes), 
                                                            system="codec")
            return None
        frames = list(unpack('160h', bytes))
        return self.enc.encode(frames)

    def decode(self, bytes):
        if len(bytes) != 40:
            log.msg("speex: short read on decode %d != 40"%len(bytes), 
                                                            system="codec")
            return None
        frames = self.dec.decode(bytes)
        ostr = struct.pack('160h', *frames)
        return ostr

class MulawCodec(_Codec):
    "A codec for mulaw encoded audio (e.g. G.711U)"

    def encode(self, bytes):
        if len(bytes) != 320:
            log.msg("mulaw: short read on encode, %d != 320"%len(bytes), 
                                                            system="codec")
        return audioop.lin2ulaw(bytes, 2)

    def decode(self, bytes):
        if len(bytes) != 160:
            log.msg("mulaw: short read on decode, %d != 160"%len(bytes), 
                                                            system="codec")
        return audioop.ulaw2lin(bytes, 2)

class AlawCodec(_Codec):
    "A codec for alaw encoded audio (e.g. G.711A)"

    def encode(self, bytes):
        if len(bytes) != 320:
            log.msg("alaw: short read on encode, %d != 320"%len(bytes), 
                                                            system="codec")
        return audioop.lin2alaw(bytes, 2)

    def decode(self, bytes):
        if len(bytes) != 160:
            log.msg("alaw: short read on decode, %d != 160"%len(bytes), 
                                                            system="codec")
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
            self.codecs[PT_SPEEX] = SpeexCodec()
        #if codecs.dvi4 is not None:
        #    self.codecs[PT_DVI4] = DVI4Codec()
        #if codecs.ilbc is not None:
        #    self.codecs[PT_ILBC] = ILBCCodec()

    def getDefaultFormat(self):
        return self.format

    def setDefaultFormat(self, format, noexc=False):
        if (isinstance(format, AudioPTMarker)
                and format not in (PT_CN, PT_xCN)
                and self.codecs.has_key(format)):
            self.format = format
            return True
        elif noexc:
            return False
        else:
            raise ValueError("Can't handle codec %r"%format)

    def encode(self, bytes):
        "Accepts audio as bytes, emits an RTPPacket"
        if not bytes:
            return None
        codec = self.codecs.get(self.format)
        if not codec:
            raise ValueError("can't encode format %r"%self.format)
        encaudio = codec.encode(bytes)
        if not encaudio:
            return None
        return RTPPacket(0, 0, 0, encaudio, ct=self.format)

    def decode(self, packet):
        "Accepts an RTPPacket, emits audio as bytes"
        if not packet.data:
            return None
        codec = self.codecs.get(packet.header.ct)
        if not codec:
            raise ValueError("can't decode format %r"%packet.header.ct)
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
        if type(fmt) is not list:
            fmt = [fmt]
        for f in fmt:
            res = self.codecker.setDefaultFormat(f, noexc=True)
            if res:
                break
        else:
            raise ValueError("No working formats!")

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
        NullConv.reopen(self)
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
        NullConv.close(self)

class DougConverter(MediaLayer):
    "Specialised converter for Doug."
    # XXX should be refactored away to just use a Codecker directly
    def __init__(self, defaultFormat=PT_PCMU, *args, **kwargs):
        self.codecker = Codecker()
        self.codecker.setDefaultFormat(defaultFormat)
        self.convertOutbound = self.codecker.encode
        self.convertInbound = self.codecker.decode
        if not kwargs.get('device'):
            kwargs['device'] = None
        NullConv.__init__(self, *args, **kwargs)
