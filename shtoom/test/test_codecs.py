
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
    def isOpen(self):
        return False
    pass

class CodecTest(unittest.TestCase):

    def testCodeckerSanity(self):
        a_ = self.assert_
        ae = self.assertEquals
        ar = self.assertRaises
        c = Codecker(PT_PCMU)
        a_(isinstance(c.format_to_codec.get(PT_PCMU), MulawCodec))
        a_(isinstance(c.format_to_codec.get(PT_RAW), PassthruCodec))
        a_(isinstance(c.format_to_codec.get(PT_CN), NullCodec))
        for codec in c.format_to_codec.values():
            a_(isinstance(codec, _Codec))
        ae(c.getDefaultFormat(), PT_PCMU)
        ar(ValueError, Codecker, PT_QCELP)

    def testNullCodec(self):
        ae = self.assertEquals
        ar = self.assertRaises
        n = NullCodec()
        ae(n._encode('frobozulate'), None)
        ae(n.decode('frobozulate'), None)
        ar(ValueError, Codecker, PT_CN)

    def testPassthruCodec(self):
        ae = self.assertEquals
        c = Codecker(PT_RAW)
        ae(c.getDefaultFormat(), PT_RAW)
        p = PassthruCodec()
        ae = self.assertEquals

        class Foo:
            def handle_media_sample(self, sample):
                ae(sample.data, 'frobozulate')
        c.set_handler(Foo().handle_media_sample)

        c.handle_audio('frobozulate')

        class Foo:
            def handle_media_sample(self, sample):
                ae(sample.data, 'farnarkling')
                ae(sample.ct, PT_RAW)
        c.set_handler(Foo().handle_media_sample)

        c.handle_audio('farnarkling')

    # XXX testing other codecs - endianness issues? crap.

    def testMuLawCodec(self):
        if codecs.mulaw is None:
            raise unittest.SkipTest("no mulaw support")
        ae = self.assertEquals
        c = Codecker(PT_PCMU)
        ae(c.getDefaultFormat(), PT_PCMU)

        class Foo:
            def handle_media_sample(self, sample):
                ae(len(sample.data), 160)
                ae(sample.data, ulawout)
                ae(sample.ct, PT_PCMU)
        c.set_handler(Foo().handle_media_sample)
        c.handle_audio(instr)

    def testGSMCodec(self):
        if codecs.gsm is None:
            raise unittest.SkipTest("no gsm support")
        ae = self.assertEquals
        c = Codecker(PT_GSM)
        ae(c.getDefaultFormat(), PT_GSM)

        class Foo:
            def handle_media_sample(self, sample):
                ae(len(sample.data), 33)
                ae(sample.ct, PT_GSM)
                p = RTPPacket(0, 0, 0, data=sample.data, ct=sample.ct)
                ae(len(c.decode(p)), 320)
        c.set_handler(Foo().handle_media_sample)

        c.handle_audio(instr)

        c = Codecker(PT_GSM)
        ae(c.getDefaultFormat(), PT_GSM)

        class Foo:
            def handle_media_sample(self, sample, tester=self):
                tester.fail("WRONG.  The decoding of 32 zeroes (a short GSM frame) is required to be None, but it came out: %s" % (sample,))
        c.set_handler(Foo().handle_media_sample)

        c.handle_audio('\0'*32)

    def testSpeexCodec(self):
        if codecs.gsm is None:
            raise unittest.SkipTest("no speex support")
        ae = self.assertEquals
        c = Codecker(PT_SPEEX)
        ae(c.getDefaultFormat(), PT_SPEEX)

        class Foo:
            def handle_media_sample(self, sample):
                ae(len(sample.data), 40)
                ae(sample.ct, PT_SPEEX)
                p = RTPPacket(0, 0, 0, data=sample.data, ct=sample.ct)
                ae(len(c.decode(p)), 320)
        c.set_handler(Foo().handle_media_sample)

        p = c.handle_audio(instr)

        class Foo:
            def handle_media_sample(self, sample, tester=self):
                tester.fail("WRONG.  The decoding of 30 zeroes (a short Speex frame) is required to be None, but it came out: %s" % (sample,))
        c.set_handler(Foo().handle_media_sample)

        c.handle_audio('\0'*30)

    def testMediaLayer(self):
        ae = self.assertEquals
        dev = DummyDev()
        m = MediaLayer(device=dev)
        m.selectDefaultFormat([PT_PCMU,])
        ae(m.getDevice(), dev)
        ae(m.getFormat(), PT_PCMU)
        m = MediaLayer(device=dev)
        m.selectDefaultFormat([PT_RAW,])
        ae(m.getFormat(), PT_RAW)

    def testDougConverter(self):
        ae = self.assertEquals
        d = DougConverter(device=DummyDev())
        d.selectDefaultFormat([PT_RAW,])
        ae(d.getFormat(), PT_RAW)
        test='froooooooooooogle'
        p = RTPPacket(0, 0, 0, data=test, ct=PT_RAW)
        ae(d.convertInbound(p), test)


ulawout = '\x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 \x9f\x87\x07 '
