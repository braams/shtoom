
# Massive hackage. This is a proof-of-concept, only.
# Feed it hostname, port, and an audio file (in 8bit ulaw - sox -t ul)
# Or skip the audio file and it'll read from the microphone
# See also rtprecv.py for something that listens to a port and dumps it to
# the audio device

import time, signal, socket, struct
from time import time, sleep

USE_SETITIMER = 1


import itimer
from twisted.internet import reactor

def getAudioDevice():
    import ossaudiodev
    dev = ossaudiodev.open('rw')
    dev.speed(8000)
    dev.nonblock()
    dev.channels(1)
    dev.setfmt(ossaudiodev.AFMT_MU_LAW)
    return dev

out = 0

def genSSRC():
    # Python-ish hack at RFC1889, Appendix A.6
    import md5, time, os, socket
    m = md5.new()
    m.update(str(time.time()))
    m.update(str(os.getuid()))
    m.update(str(os.getgid()))
    m.update(str(socket.gethostname()))
    hex = m.hexdigest()
    nums = hex[:8], hex[8:16], hex[16:24], hex[24:]
    nums = [ int(x, 16) for x in nums ]
    ssrc = 0
    for n in nums: ssrc = ssrc ^ n
    return ssrc

def genInitTS():
    # Python-ish hack at RFC1889, Appendix A.6
    import md5, time, os, socket
    m = md5.new()
    m.update(str(genSSRC()))
    m.update(str(time.time()))
    hex = m.hexdigest()
    nums = hex[:8], hex[8:16], hex[16:24], hex[24:]
    nums = [ int(x, 16) for x in nums ]
    ts = 0
    for n in nums: ts = ts ^ n
    return ts

def getRandom(bits):
    import md5
    m = md5.new()
    m.update(open('/dev/urandom').read(128))
    hex = m.hexdigest()
    random = int(hex[:bits//4],16)
    return random

class FixedSender:
    def __init__(self, sock, data):
        self.sock = sock
        self.data = data
        self.maxoff = len(self.data)
        self.offs = 0
        self.caught = []
    def nextpacket(self, n, f, time=time):
        self.sock.sendto(self.data[self.offs:self.offs+160], ('',9010))
        self.offs += 160
        if self.offs >= self.maxoff:
            itimer.setitimer(itimer.ITIMER_REAL, 0.0, 0.0)
            global out
            print "and we're out..."
            out = 1

class AudioSender:
    def __init__(self, sock, dest, fp=None):
        self.sock = sock
        if fp is None:
            self.fp = getAudioDevice()
        else:
            self.fp = fp
        self.seq = getRandom(bits=16)
        self.ts = genInitTS()
        self.ssrc = genSSRC()
        self.sample = None
        self.packets = 0
        self.sent = 0
        self.last = None

    def nextpacketTwisted(self, reactor=reactor):
        # 10ms clock resolution - setting to 15ms means we always hit it.
        reactor.callLater(0.015, self.nextpacketTwisted)
        t = time()
        if self.last is not None:
            print "%d"%(1000*(t- self.last))
        self.last = t
        self.nextpacket(None, None)

    def nextpacket(self, n, f, pack=struct.pack):
        self.packets += 1
        if self.sample is not None:
            self.sent += 1
            hdr = pack('!BBHII', 0x80, 0x0, self.seq, self.ts, self.ssrc)
            self.sock.sendto(hdr+self.sample, ('',9010))
            self.sample = None
        self.seq += 1
        self.ts += 160
        try:
            self.sample = self.fp.read(160)
        except IOError:
            pass

def main():
    import sys
    rsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    rsock.bind(('',0))
    print "Bound to port", rsock.getsockname()[1]
    if len(sys.argv) == 4:
        C = AudioSender(rsock, (sys.argv[1], sys.argv[2]), open(sys.argv[3]))
    else:
        C = AudioSender(rsock, (sys.argv[1], sys.argv[2]))
    if USE_SETITIMER:
        signal.signal(signal.SIGALRM, C.nextpacket)
        itimer.setitimer(itimer.ITIMER_REAL, 0.02, 0.02)
    else:
        from twisted.internet import reactor
        reactor.callLater(0.02, C.nextpacketTwisted)
        
    start = time()
    if USE_SETITIMER:
        try:
            while out == 0:
                sleep(2)
                print "%s/%s - missed %s"%(C.sent, C.packets, (C.packets-C.sent))
        except KeyboardInterrupt:
            pass
    else:
        reactor.run()
    if USE_SETITIMER:
        itimer.setitimer(itimer.ITIMER_REAL, 0.0, 0.0)
    import resource
    rusage = resource.getrusage(resource.RUSAGE_SELF)
    print "%f %f, %ds"%(rusage[0], rusage[1], time()-start )

if __name__ == "__main__":
    main()
