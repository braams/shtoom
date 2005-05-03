#!/usr/bin/env python


import math, random, struct, sys
sys.path.append(sys.path.pop(0))
import shtoom.audio
from shtoom.rtp import formats

from shtoom.rtp.packets import RTPPacket

app = None

class Recorder:
    def __init__(self, dev, play=False, outfp=None):
        self._dev = dev
        self._play = play
        self._outfp = outfp
        self.seq = random.randrange(0, 2**48)
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

    def handle_media_sample(self, sample):
        if not sample:
            print "no audio, skipping"
            return
        if self._outfp:
            self._outfp.write(sample.data)
        if self._play:
            packet = RTPPacket(0, self.seq, 0, data=sample.data, ct=sample.ct)
            self.seq = (self.seq + 1) % 2**48
            self._dev.write(packet)
        #if len(packet.data) != 320:
        #    print "discarding bad length (%d) packet"%(len(packet.data))
        #else:
        #    self.analyse(struct.unpack('160h', packet.data))


def main(Recorder = Recorder):
    from shtoom.audio import getAudioDevice
    from shtoom.rtp import formats
    from twisted.internet.task import LoopingCall
    from twisted.internet import reactor
    from twisted.python import log
    import sys
    log.startLogging(sys.stdout)

    dev = getAudioDevice()
    dev.close()
    if len(sys.argv) > 1:
        fmt = sys.argv[1]
        if not hasattr(formats, fmt):
            print "unknown PT marker %s"%(fmt)
            sys.exit(1)
        dev.selectDefaultFormat([getattr(formats,fmt),])
    else:
        dev.selectDefaultFormat([formats.PT_RAW,])
    rec = Recorder(dev, play=True)
    dev.reopen(mediahandler=rec.handle_media_sample)

    reactor.run()

if __name__ == "__main__":
    main()
