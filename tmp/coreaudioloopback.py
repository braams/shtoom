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
    inbuffer = ''
    outbuffer = ''
    SCALE = 32768/2

    def toStdFmt(self, buffer):
        b = buffer * self.SCALE - self.SCALE/2
        b = b.astype(Int16)
        # Damn. Endianness?  
        b = b.tostring()
        b, self.tostate = audioop.ratecv(b, 2, 2, 44100, 8000, self.tostate)
        b = audioop.tomono(b, 2, 1, 1)
        return b

    def to44Kstereo(self, buffer):
        b = audioop.tostereo(buffer, 2, 1, 1)
        b, self.fromstate = audioop.ratecv(b, 2, 2, 8000, 44100, self.fromstate)
        return b

    def fromPCMString(self, buffer):
        from numarray import fromstring, Int16, Float32
        b = fromstring(buffer, Int16)
        b = b.astype(Float32)
        b = ( b + 32768/2 ) / self.SCALE
        return b

    def callback(self, buffer):
        if self.offset % 100 == 0:
            now = time()
            print len(buffer), now-self.prevtime
            self.prevtime = now
        self.offset += 1
        try:
            std = self.toStdFmt(buffer)
            print "converted 512 samples to %d bytes"%(len(std))
            out = self.to44Kstereo(std)
            print "and back to %d bytes"%(len(out))
            self.inbuffer += out
            if len(self.inbuffer)  < 2048:
                buffer[:] = zeros(1024)
                return
            else:
                std, self.inbuffer = self.inbuffer[:2048], self.inbuffer[2048:]
                out = self.fromPCMString(std)
                #print "producing %d samples"%len(out)
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

class LC:
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
    lc = LC()
    reactor.callLater(0, lc.go)
    reactor.run()
    print "stopping"
    coreaudio.stopAudio(ap)

if __name__ == "__main__":
    main()
