#!/usr/bin/env python2.3


import struct, math, sys
sys.path.append(sys.path.pop(0))
import shtoom.audio

app = None

class Recorder:
    def __init__(self, dev, play=False, outfp=None):
        self._dev = dev
        self._play = play
        self._outfp = outfp
	import sys
        if '-q' in sys.argv:
            self.quiet = True
        else:
            self.quiet = False

    def analyse(self, samples):
        if self.quiet: 
            return
        sampcount = len(samples)
        abssamp = [ abs(x) for x in samples ]
        mean = sum(abssamp)/sampcount
        s = reduce(lambda x,y: x+(y*y), samples)
        ms = s/sampcount
        rms = math.sqrt(ms)
        deviations = [ mean-x for x in abssamp ]
        var = reduce(lambda x,y: x+(y*y), deviations)/float(sampcount - 1)
        std = math.sqrt(var)
        #print "Mean % 5d  RMS % 5d STD % 3d"%(mean,rms,std)
        return 

    def sample(self, *args):
        try:
            data = self._dev.read()
        except IOError:
            return
        if not data:
            print "no audio, skipping"
            return
        if self._outfp:
            self._outfp.write(data)
        if self._play:
            self._dev.write(data, shtoom.audio.FMT_RAW)
        if len(data) != 320:
            print "discarding bad length (%d) packet"%(len(data))
        else:
            self.analyse(struct.unpack('160h', data))


def main(Recorder = Recorder):
    from shtoom.audio import getAudioDevice, FMT_RAW
    from twisted.internet.task import LoopingCall
    from twisted.internet import reactor
    import sys

    dev = getAudioDevice('rw')
    dev.close()
    dev.reopen()
    dev.selectFormat(FMT_RAW)
    #if len(sys.argv) > 1:
    #    outfp = open(sys.argv[1], 'wb')
    #else:
    outfp = None
    rec = Recorder(dev, play=True, outfp=outfp)

    LC = LoopingCall(rec.sample)
    LC.start(0.020)
    reactor.run()
    if outfp:
        outfp.close()

if __name__ == "__main__":
    main()