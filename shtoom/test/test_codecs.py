
from twisted.trial import unittest

from shtoom.audio.converters import Codecker, _Codec, MediaLayer, DougConverter
from shtoom.audio.converters import MulawCodec, NullCodec, PassthruCodec
from shtoom.rtp.formats import PT_PCMU, PT_RAW, PT_CN, PT_QCELP, PT_GSM
from shtoom.rtp.packets import RTPPacket

from shtoom.avail import codecs

instr = ''.join([chr(x*32) for x in range(8)]) * 40

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
        c = Codecker()
        c.setDefaultFormat(PT_CN)
        ae(c.getDefaultFormat(), PT_CN)
        n = NullCodec()
        ae = self.assertEquals
        ae(n.encode('frobozulate'), None)
        ae(n.decode('frobozulate'), None)
        p = RTPPacket(PT_CN, '\x00', ts=None)
        ae(c.decode(p), None)
        ae(c.encode(None), None)
        ae(c.encode('\x00'), None)

    def testPassthruCodec(self):
        ae = self.assertEquals
        c = Codecker()
        c.setDefaultFormat(PT_RAW)
        ae(c.getDefaultFormat(), PT_RAW)
        p = PassthruCodec()
        ae = self.assertEquals
        ae(p.encode('frobozulate'), 'frobozulate')
        ae(p.decode('frobozulate'), 'frobozulate')
        p = RTPPacket(PT_RAW, 'farnarkling', ts=None)
        ae(c.decode(p), 'farnarkling')
        ae(c.encode('farnarkling').data, 'farnarkling')
        ae(c.encode('farnarkling').pt, PT_RAW)

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
        ae(c.encode(instr).pt, PT_PCMU)

    def testGSMCodec(self):
        if codecs.gsm is None:
            raise unittest.SkipTest("no gsm support")
        ae = self.assertEquals
        c = Codecker()
        c.setDefaultFormat(PT_GSM)
        ae(c.getDefaultFormat(), PT_GSM)
        p = c.encode(instr)
        ae(len(p.data), 33)
        ae(p.pt, PT_GSM)
        ae(len(c.decode(p)), 320)


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
