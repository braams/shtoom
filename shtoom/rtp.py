# Feed it hostname, port, and an audio file (in 8bit ulaw - sox -t ul)
# Or skip the audio file and it'll read from the microphone
# See also rtprecv.py for something that listens to a port and dumps it to
# the audio device
#
# 'use_setitimer' will give better results - needs
# http://polykoira.megabaud.fi/~torppa/py-itimer/
# $Id: rtp.py,v 1.16 2003/11/20 09:42:50 anthonybaxter Exp $
#

import signal, struct, random, os, md5, socket
from time import sleep, time

from select import select as Select

try:
    import itimer
except ImportError:
    itimer = None

from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol

from shtoom.audio import getAudioDevice


class LoopingCall:
    """Move into twisted if this helps."""
    def __init__(self, f, *a, **kw):
        self.f = f
        self.a = a
        self.kw = kw
        self.running = True

    def loop(self, interval):
        self._loop(time(), 0, interval)

    def stop(self):
        self.running = False
        if hasattr(self, "call"):
            self.call.cancel()
    
    def _loop(self, starttime, count, interval):
        if hasattr(self, "call"):
            del self.call
        self.f(*self.a, **self.kw)
        now = time() 
        while self.running:
            count += 1
            fromStart = count * interval
            fromNow = starttime - now
            delay = fromNow + fromStart
            if delay > 0:
                self.call = reactor.callLater(delay, self._loop, starttime, count, interval)
                return


class RTPProtocol(DatagramProtocol):
    """Implementation of the RTP protocol.

    Also manages a RTCP instance.
    """
    
    if itimer:
        use_setitimer = 1
    else:
        use_setitimer = 0
    use_setitimer = 0
    _cbDone = None
    infp = None
    outfp = None
    collectStats = 0
    statsIn = []
    statsOut = []

    def createRTPSocket(self):
        """Start listening on UDP ports for RTP and RTCP.

        Return (rtpPortNo, rtcpPortNo).
        """
        from twisted.internet.error import CannotListenError
        import rtcp
        self.RTCP = rtcp.RTCPProtocol()

        # RTP port must be even, RTCP must be odd
        rtpPort = 30000 + random.randint(0, 20000)
        if (rtpPort % 2) == 1:
            rtpPort += 1
        while True:
            try:
                self.rtpListener = reactor.listenUDP(rtpPort, self)
            except CannotListenError:
                rtpPort += 2
                continue
            else:
                break
        
        rtcpPort = rtpPort + 1
        while True:
            try:
                self.rtcpListener = reactor.listenUDP(rtcpPort, self.RTCP)
            except CannotListenError:
                self.rtpListener.stopListening()
                rtpPort = rtpPort + 2
                rtcpPort = rtpPort + 1
                continue
            else:
                break
        #self.rtpListener.stopReading()
        return (rtpPort, rtcpPort)

    def whenDone(self, cbDone):
        self._cbDone = cbDone

    def stopSendingAndReceiving(self):
        self.Done = 1
        self.rtpListener.stopListening()
        self.rtcpListener.stopListening()
        if self.infp:
            self.infp.close()
            self.infp = None
        if self.outfp:
            self.outfp.close()
            self.outfp = None

    def startReceiving(self, fp=None):
        if fp is None:
            self.outfp = getAudioDevice('w')
        else:
            self.outfp = fp

    def startSending(self, dest, fp=None):
        self.dest = dest
        if fp is None:
            self.infp = getAudioDevice('r')
        else:
            self.infp = fp
        self.sendFirstData()

    def startSendingAndReceiving(self, dest, fp=None):
        self.dest = dest
        if fp is None:
            self.infp = getAudioDevice('rw')
        else:
            self.infp = fp
        self.outfp = self.infp
        #self.infp = open('tmp/quake.ul','rb')
        self.prevInTime = self.prevOutTime = time()
        self.sendFirstData()

    def sendFirstData(self):
        self.seq = self.genRandom(bits=16)
        self.ts = self.genInitTS()
        self.ssrc = self.genSSRC()
        self.sample = None
        self.packets = 0
        self.Done = 0
        self.sent = 0
        try:
            self.sample = self.infp.read(160)
        except IOError: # stupid sound devices
            self.sample = None
            pass
        self.LC = LoopingCall(self.nextpacket)
        self.LC.loop(0.020)
        if self.use_setitimer:
            signal.signal(signal.SIGALRM, self.reactorWakeUp)
            itimer.setitimer(itimer.ITIMER_REAL, 0.009, 0.009)

    def reactorWakeUp(self, n, f, reactor=reactor):
        reactor.wakeUp()

    def datagramReceived(self, datagram, addr, unpack=struct.unpack):
        if self.collectStats:
            t = time()
            self.statsIn.append(str(int((t-self.prevInTime)*1000)))
            self.prevInTime = t
            if len(self.statsIn) == 100:
                print "Input", " ".join(self.statsIn)
                self.statsIn = []
        if self.outfp:
            hdr = struct.unpack('!BBHII', datagram[:12])
            if hdr[1] != 0:
                # Non-mulaw.
                print "datagram len %d, HDR: %02x %02x"%(len(datagram),hdr[0],hdr[1])
            else:
                try:
                    self.outfp.write(datagram[12:])
                except IOError:
                    pass

    def genSSRC(self):
        # Python-ish hack at RFC1889, Appendix A.6
        m = md5.new()
        m.update(str(time()))
        m.update(str(os.getuid()))
        m.update(str(os.getgid()))
        m.update(str(socket.gethostname()))
        hex = m.hexdigest()
        nums = hex[:8], hex[8:16], hex[16:24], hex[24:]
        nums = [ int(x, 16) for x in nums ]
        ssrc = 0
        for n in nums: ssrc = ssrc ^ n
        return ssrc

    def genInitTS(self):
        # Python-ish hack at RFC1889, Appendix A.6
        m = md5.new()
        m.update(str(self.genSSRC()))
        m.update(str(time()))
        hex = m.hexdigest()
        nums = hex[:8], hex[8:16], hex[16:24], hex[24:]
        nums = [ int(x, 16) for x in nums ]
        ts = 0
        for n in nums: ts = ts ^ n
        return ts

    def genRandom(self, bits):
        """Generate up to 128 bits of randomness."""
        if os.path.exists("/dev/urandom"):
            hex = open('/dev/urandom').read(16).encode("hex")
        else:
            m = md5.new()
            m.update(str(time()))
            m.update(str(random.random()))
            m.update(str(id(self.dest)))
            hex = m.hexdigest()
        return int(hex[:bits//4],16)

    def nextpacket(self, n=None, f=None, pack=struct.pack):
        if self.Done:
            self.LC.stop()
            if self.use_setitimer:
                itimer.setitimer(itimer.ITIMER_REAL, 0.0, 0.0)
            if self._cbDone:
                self._cbDone()
            return
        self.packets += 1
        if self.sample is not None:
            self.sent += 1
            # This bit is hardcoded for G711 ULAW. When other codecs are
            # done, the first two bytes will change (but should be mostly
            # constant across a RTP session).
            hdr = pack('!BBHII', 0x80, 0x0, self.seq, self.ts, self.ssrc)
            t = time()
            self.transport.write(hdr+self.sample, self.dest)
            self.sample = None
        else:
            print "skipping audio, %s/%s sent"%(self.sent, self.packets)
        if self.collectStats:
            t = time()
            self.statsOut.append(str(int((t-self.prevOutTime)*1000)))
            self.prevOutTime = t
            if len(self.statsOut) == 100:
                print "Output", " ".join(self.statsOut)
                self.statsOut = []
        self.seq += 1
        self.ts += 160
        try:
            if self.infp:
                self.sample = self.infp.read(160)
        except IOError:
            pass
        
        if (self.sample is not None) and (len(self.sample) == 0):
            print "And we're done!"
            self.Done = 1
