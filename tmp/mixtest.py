#!/usr/bin/env python2.3

import shtoom.audio
import shtoom.rtp.formats
import struct, math, sys, time

from twisted.internet import reactor

import numarray


class Recorder:
    def __init__(self, dev, outfp, mixins=[] ):
        self._dev = dev
        self._outfp = outfp
        self.mixins = mixins


    def mixPyrex(self, samples, time=time.time, unpack=struct.unpack):
        import mix
        divider = min(len(samples), 4)
        if divider == 1:
            return samples[0]
        t1 = time()
        samples = [ unpack('160h', x) for x in samples]
        t2 = time()
        samples = [ mix.power(x) for x in samples ]
        samples.sort() ; samples.reverse()
        samples = [ x[1] for x in samples[:4] ]
        t3 = time()
        divsamples = []
        for sample in samples:
            divsample = [ x/divider for x in sample ]
            divsamples.append(divsample)
        t4 = time()
        ds = map(None, *divsamples)
        out = map(sum, ds)
        t4 = time()
        print "time %.2f: ctor %.2f pow %.2f combin %.2f"%(
                        (t4-t1) * 1000,
                        (t2-t1) * 1000,
                        (t3-t2) * 1000,
                        (t4-t3) * 1000,
                             )
        out = struct.pack('160h', *out)
        return out

    def powerPsyco(self, sample):
        sampcount = len(sample)
        s = sum([x * x for x in sample])
        ms = s/sampcount
        rms = math.sqrt(ms)
        return rms, sample

    def mixPsyco(self, samples, time=time.time, unpack=struct.unpack):
        divider = min(len(samples), 4)
        if divider == 1:
            return samples[0]
        t1 = time()
        samples = [ unpack('160h', x) for x in samples]
        t2 = time()
        samples = [ self.powerPython(x) for x in samples ]
        samples.sort() ; samples.reverse()
        samples = [ x[1] for x in samples[:4] ]
        t3 = time()
        divsamples = []
        for sample in samples:
            divsample = [ x/divider for x in sample ]
            divsamples.append(divsample)
        t4 = time()
        ds = map(None, *divsamples)
        out = map(sum, ds)
        t5 = time()
        print "time %.2f: ctor %.2f pow %.2f div %.2f add %.2f"%(
                        (t5-t1) * 1000,
                        (t2-t1) * 1000,
                        (t3-t2) * 1000,
                        (t4-t3) * 1000,
                        (t5-t4) * 1000,
                             )
        out = struct.pack('160h', *out)
        return out

        psyco.bind(mixPsyco)
        psyco.bind(powerPsyco)


    def powerPython(self, sample):
        sampcount = len(sample)
        s = sum([x * x for x in sample])
        ms = s/sampcount
        rms = math.sqrt(ms)
        return rms, sample

    def mixPython(self, samples, time=time.time, unpack=struct.unpack):
        divider = min(len(samples), 4)
        if divider == 1:
            return samples[0]
        t1 = time()
        samples = [ unpack('160h', x) for x in samples]
        t2 = time()
        samples = [ self.powerPython(x) for x in samples ]
        samples.sort() ; samples.reverse()
        samples = [ x[1] for x in samples[:4] ]
        t3 = time()
        divsamples = []
        for sample in samples:
            divsample = [ x/divider for x in sample ]
            divsamples.append(divsample)
        t4 = time()
        ds = map(None, *divsamples)
        out = map(sum, ds)
        t5 = time()
        print "time %.2f: ctor %.2f pow %.2f div %.2f add %.2f"%(
                        (t5-t1) * 1000,
                        (t2-t1) * 1000,
                        (t3-t2) * 1000,
                        (t4-t3) * 1000,
                        (t5-t4) * 1000,
                             )
        out = struct.pack('160h', *out)
        return out


    def powerNumeric(self, sample):
        from numarray import add, Int32, power, array, multiply
        s = sample.astype(Int32)
        multiply(s, s, s)
        ms = add.reduce(s)/160
        rms = math.sqrt(ms)
        return rms, id(sample), sample

    def mixNumeric(self, samples, time=time.time):
        from numarray import add, array, Int16, fromstring
        divider = min(len(samples), 4)
        if divider == 1:
            return samples[0]
        t1 = time()
        samples = [ fromstring(x, Int16) for x in samples ]
        t2 = time()
        samples = [ self.powerNumeric(x) for x in samples ]
        samples.sort() ; samples.reverse()
        samples = [ x[2] for x in samples[:4] ]
        t3 = time()
        divsamples = [ x/divider for x in samples ]
        t4 = time()
        out = reduce(add, divsamples)
        t5 = time()
        print "time %.2f: ctor %.2f pow %.2f div %.2f add %.2f"%(
                        (t5-t1) * 1000,
                        (t2-t1) * 1000,
                        (t3-t2) * 1000,
                        (t4-t3) * 1000,
                        (t5-t4) * 1000,
                    )
        return out.tostring()

    def mixAudioOp(self, samples, time=time.time):
        import audioop
        t1 = time()
        power = [ (audioop.rms(x,2),x) for x in samples ]
        power.sort(); power.reverse()
        samples = [ x[1] for x in power[:4] ]
        t2 = time()
        divsamples = [ audioop.mul(x, 2, len(samples)) for x in samples ]
        t3 = time()
        out = reduce(lambda x,y: audioop.add(x, y, 2), divsamples)
        t4 = time()
        print "time %.2f: pow %.2f div %.2f add %.2f"%(
                        (t4-t1) * 1000,
                        (t2-t1) * 1000,
                        (t3-t2) * 1000,
                        (t4-t3) * 1000,
                    )
        return out

    mix = mixNumeric

    def sample(self, unpack=struct.unpack, pack=struct.pack):
        if self._outfp is not None:
            try:
                indata = self._dev.read()
            except IOError:
                return
            if len(indata) != 320:
                print "discarding short (%d) packet"%(len(indata))
                return
        samples = [ x.read(320) for x in self.mixins ]
        if self._outfp is not None:
            samples.append(indata)
        new = self.mix(samples)
        if self._outfp is not None:
            self._outfp.write(indata)
        self._dev.write(new, shtoom.rtp.formats.PT_RAW)

    def stop(self):
        print "Stopping"
        if self._outfp is not None:
            self._outfp.close()
        del self._outfp
        LC.stop()
        reactor.stop()

def main(Recorder = Recorder):
    from shtoom.audio import getAudioDevice, formats
    from twisted.internet.task import LoopingCall
    import sys
    global LC

    dev = getAudioDevice()
    dev.close()
    dev.reopen()
    dev.selectDefaultFormat(formats.PT_RAW)
    #outfp = open(sys.argv[1], 'wb')
    mixins = [ open(x, 'rb') for x in sys.argv[2:] ]
    rec = Recorder(dev, mixins=mixins, outfp=None)

    LC = LoopingCall(rec.sample)
    LC.start(0.020)
    print "starting"
    reactor.callLater(10, rec.stop)
    reactor.run()

if __name__ == "__main__":
    main()
