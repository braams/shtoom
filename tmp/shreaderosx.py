#!/usr/bin/env python2.3

# 
# A modfied versin of shreadder that does the correct magic for 
# OSX. Also works through a MediaLayer.
#

import struct, math, sys
sys.path.append(sys.path.pop(0))
import shtoom.audio
from shtoom.rtp import formats

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
            packet = self._dev.read()
        except IOError:
            return
        if not packet:
            #print "no audio, skipping"
            return
        if self._outfp:
            self._outfp.write(packet.data)
        if self._play:
            self._dev.write(packet)
        #if len(packet.data) != 320:
        #    print "discarding bad length (%d) packet"%(len(packet.data))
        #else:
        #    self.analyse(struct.unpack('160h', packet.data))


def main(Recorder = Recorder):
    from shtoom.audio import tcpaudio
    from shtoom.audio.converters import MediaLayer
    from shtoom.rtp import formats
    from twisted.internet.task import LoopingCall
    from twisted.internet import reactor
    import sys

    dev = MediaLayer(tcpaudio.TCPAudioDevice())
    dev.close()
    dev.reopen()
    if len(sys.argv) > 1:
        fmt = sys.argv[1]
        if not hasattr(formats, fmt):
            print "unknown PT marker %s"%(fmt)
            sys.exit(1)
        dev.selectDefaultFormat(getattr(formats,fmt))
    else:
        dev.selectDefaultFormat(formats.PT_PCMU)
    outfp = None
    rec = Recorder(dev, play=True, outfp=outfp)

    LC = LoopingCall(rec.sample)
    LC.start(0.02)
    reactor.run()
    if outfp:
        outfp.close()

if __name__ == "__main__":
    main()
