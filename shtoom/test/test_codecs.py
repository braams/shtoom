
from twisted.trial import unittest

from shtoom.audio.converters import Codecker, _Codec, MediaLayer, DougConverter
from shtoom.audio.converters import MulawCodec, NullCodec, PassthruCodec
from shtoom.rtp.formats import PT_PCMU, PT_RAW, PT_CN, PT_QCELP, PT_GSM, PT_SPEEX
from shtoom.rtp.packets import RTPPacket

from shtoom.avail import codecs

from shtoom.audio.converters import isLittleEndian
instr = ''.join([chr(x*32) for x in range(8)]) * 40
if not isLittleEndian():
    import array
    a = array.array('H')
    a.fromstring(instr)
    a.byteswap()
    instr = a.tostring()

class DummyDev:
    # Should have read/write
    pass

class CodecTest(unittest.TestCase):

    def testCodeckerSanity(self):
        a_ = self.assert_
        ae = self.assertEquals
        ar = self.assertRaises
        c = Codecker()
        a_(isinstance(c.codecs.get(PT_PCMU), MulawCodec))
        a_(isinstance(c.codecs.get(PT_RAW), PassthruCodec))
        a_(isinstance(c.codecs.get(PT_CN), NullCodec))
        for codec in c.codecs.values():
            a_(isinstance(codec, _Codec))
        c.setDefaultFormat(PT_PCMU)
        ae(c.getDefaultFormat(), PT_PCMU)
        c.setDefaultFormat(PT_PCMU)
        ar(ValueError, c.setDefaultFormat, PT_QCELP)

    def testNullCodec(self):
        ae = self.assertEquals
        ar = self.assertRaises
        n = NullCodec()
        ae(n.encode('frobozulate'), None)
        ae(n.decode('frobozulate'), None)
        c = Codecker()
        ar(ValueError, c.setDefaultFormat, PT_CN)

    def testPassthruCodec(self):
        ae = self.assertEquals
        c = Codecker()
        c.setDefaultFormat(PT_RAW)
        ae(c.getDefaultFormat(), PT_RAW)
        p = PassthruCodec()
        ae = self.assertEquals
        ae(p.encode('frobozulate'), 'frobozulate')
        ae(p.decode('frobozulate'), 'frobozulate')
        p = RTPPacket(0, 0, 0, 'farnarkling', ct=PT_RAW)
        ae(c.decode(p), 'farnarkling')
        ae(c.encode('farnarkling').data, 'farnarkling')
        ae(c.encode('farnarkling').header.pt, PT_RAW.pt)

    # XXX testing other codecs - endianness issues? crap.

    def testMuLawCodec(self):
        if codecs.mulaw is None:
            raise unittest.SkipTest("no mulaw support")
        ae = self.assertEquals
        c = Codecker()
        c.setDefaultFormat(PT_PCMU)
        ae(c.getDefaultFormat(), PT_PCMU)
        ae(len(c.encode(instr).data), 160)
        ae(c.encode(instr).data, ulawout)
        ae(c.encode(instr).header.ct, PT_PCMU)

    def testGSMCodec(self):
        if codecs.gsm is None:
            raise unittest.SkipTest("no gsm support")
        ae = self.assertEquals
        c = Codecker()
        c.setDefaultFormat(PT_GSM)
        ae(c.getDefaultFormat(), PT_GSM)
        p = c.encode(instr)
        ae(len(p.data), 33)
        ae(p.header.ct, PT_GSM)
        ae(len(c.decode(p)), 320)
        ae(c.encode('\0'*32), None)

    def testSpeexCodec(self):
        if codecs.gsm is None:
            raise unittest.SkipTest("no speex support")
        ae = self.assertEquals
        c = Codecker()
        c.setDefaultFormat(PT_SPEEX)
        ae(c.getDefaultFormat(), PT_SPEEX)
        p = c.encode(instr)
        ae(len(p.data), 40)
        ae(p.header.ct, PT_SPEEX)
        ae(len(c.decode(p)), 320)
        ae(c.encode('\0'*30), None)

    def testMediaLayer(self):
        ae = self.assertEquals
        dev = DummyDev()
        m = MediaLayer(device=dev)
        ae(m.getDevice(), dev)
        ae(m.getFormat(), PT_PCMU)
        m = MediaLayer(device=dev, defaultFormat=PT_RAW)
        ae(m.getFormat(), PT_RAW)

    def testDougConverter(self):
        ae = self.assertEquals
        d = DougConverter(device=DummyDev())
        d.selectDefaultFormat(PT_RAW)
        ae(d.getFormat(), PT_RAW)
        test='froooooooooooogle'
        ae(d.convertOutbound(test).data, test)


ulawout = '\x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 '
