import thread
## Have to initialize the threading mechanisms in order for PyGIL_Ensure to work
from twisted.python import threadable
threadable.init(1)
thread.start_new_thread(lambda: None, ())

from math import sin, sqrt
from numarray import multiply, add, Int16, zeros
import sys, traceback, audioop
from time import time
from twisted.internet import reactor

def RMS(a):
    multiply(a, a, a)
    ms = add.reduce(a)/len(a)
    rms = sqrt(ms)
    return rms

class AudioProducer(object):
    offset = 0
    prevtime = 0
    tostate = None
    fromstate = None
    # Data from the "network", waiting to be fed to the audio device
    _inbuffer = ''
    # Data from the audio device, waiting to be fed to the network
    _outbuffer = ''
    SCALE = 32768/2

    def from44KStereo(self, buffer):
        b, self.tostate = audioop.ratecv(buffer, 2, 2, 44100, 8000, self.tostate)
        b = audioop.tomono(b, 2, 1, 1)
        return b

    def toPCMString(self, buffer):
        b = buffer * self.SCALE - self.SCALE/2
        b = b.astype(Int16)
        # Damn. Endianness?
        b = b.tostring()
        return b

    def to44KStereo(self, buffer):
        b = audioop.tostereo(buffer, 2, 1, 1)
        b, self.fromstate = audioop.ratecv(b, 2, 2, 8000, 44100, self.fromstate)
        return b

    def fromPCMString(self, buffer):
        from numarray import fromstring, Int16, Float32
        print "buffer", len(buffer)
        b = fromstring(buffer, Int16)
        b = b.astype(Float32)
        b = ( b + 32768/2 ) / self.SCALE
        return b

    def maybeLoopback(self):
        if len(self._outbuffer) > 200:
            buf, self._outbuffer = self._outbuffer[:200], self._outbuffer[200:]
            buf = self.to44KStereo(buf)
            self._inbuffer = self._inbuffer + buf

    def storeSamples(self, samples):
        "Takes an array of 512 32bit float samples, stores as 8KHz 16bit ints"
        std = self.toPCMString(samples)
        std = self.from44KStereo(std)
        self._outbuffer = self._outbuffer + std
        self.maybeLoopback()

    def getSamples(self):
        "Returns an array of 512 32 bit samples"
        if len(self._inbuffer) < 2048:
            return None
        else:
            res, self._inbuffer = self._inbuffer[:2048], self._inbuffer[2048:]
            res = self.fromPCMString(res)
            return res

    def callback(self, buffer):
        if self.offset % 100 == 0:
            now = time()
            print len(buffer), now-self.prevtime
            self.prevtime = now
        self.offset += 1
        try:
            self.storeSamples(buffer)
            out = self.getSamples()
            if out is None:
                buffer[:] = zeros(1024)
                return
            else:
                buffer[:] = out
                return
        except:
            e,v,t = sys.exc_info()
            print e, v
            traceback.print_tb(t)
        return
        for frame in xrange(512):
            v = 0.5 * sin(3.1415*440.0/44100.0*(frame+(512*self.offset)))
            # Stereo
            buffer[2*frame] = v
            buffer[2*frame+1] = v

from twisted.internet.task import LoopingCall

class AudioConsumer:
    def __init__(self):
        self.start = time()

    def go(self):
        self.lc = LoopingCall(self.loop)
        self.lc.start(0.5)

    def loop(self):
        print "loop"
        if time() - self.start > 10:
            self.lc.stop()
            reactor.stop()

def main():
    import time
    import coreaudio
    ap = AudioProducer()
    coreaudio.installAudioCallback(ap)
    lc = AudioConsumer()
    reactor.callLater(0, lc.go)
    reactor.run()
    print "stopping"
    coreaudio.stopAudio(ap)

if __name__ == "__main__":
    main()
