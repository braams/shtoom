# Feed it hostname, port, and an audio file (in 8bit ulaw - sox -t ul)
# Or skip the audio file and it'll read from the microphone
# See also rtprecv.py for something that listens to a port and dumps it to
# the audio device
#
# 'use_setitimer' will give better results - needs
# http://polykoira.megabaud.fi/~torppa/py-itimer/
# $Id: rtp.py,v 1.25 2003/12/21 16:38:33 itamar Exp $
#

import signal, struct, random, os, md5, socket
from time import sleep, time

from shtoom.audio import FMT_PCMU, FMT_GSM, FMT_SPEEX, FMT_DVI4

try:
    import itimer
except ImportError:
    itimer = None

from twisted.internet import reactor, defer
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.task import LoopingCall

from shtoom.audio import getAudioDevice
from shtoom.multicast.SDP import rtpPTDict


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
    PT_pcmu = rtpPTDict[('PCMU', 8000, 1)]
    PT_gsm = rtpPTDict[('GSM', 8000, 1)]

    def createRTPSocket(self, locIP, needSTUN=False):
        """ Start listening on UDP ports for RTP and RTCP.

	    Returns a Deferred, which is triggered when the sockets are 
	    connected, and any STUN has been completed. The deferred 
	    callback will be passed (extIP, extPort).
        """
        from twisted.internet.error import CannotListenError
        import rtcp
        self.RTCP = rtcp.RTCPProtocol()

        # RTP port must be even, RTCP must be odd
        # We select a RTP port at random, and try to get a pair of ports
        # next to each other. What fun!
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
                # Not quite right - if it fails, re-do the RTP listen
                self.rtpListener.stopListening()
                rtpPort = rtpPort + 2
                rtcpPort = rtpPort + 1
                continue
            else:
                break
        #self.rtpListener.stopReading()
        if needSTUN is False:
            # The pain can stop right here
            self._extRTPPort = rtpPort
            self._extIP = locIP
            d = defer.Deferred()
            d.callback((locIP, rtpPort))
        else:
            # If the NAT is doing port translation as well, we will just 
            # have to try STUN and hope that the RTP/RTCP ports are on
            # adjacent port numbers. Please, someone make the pain stop.
            d = defer.Deferred()
            self.discoverStun(d)
	return d

    def getVisibleAddress(self):
	''' returns the local IP address used for RTP (as visible from the
	    outside world if STUN applies) as ( 'w.x.y.z', rtpPort)
	'''
        return (self._extIP, self._extRTPPort)

    def discoverStun(self, deferred):
	''' Uses STUN to discover the external address for the RTP/RTCP
            ports. deferred is a Deferred to be triggered when STUN is 
            complete.
	'''
        # See above comment about port translation.
        # We have to do STUN for both RTP and RTCP, and hope we get a sane
        # answer.
        from shtoom.stun import StunHook
        self._stunCompleteDef = deferred
        rtpDef = defer.Deferred()
        rtcpDef = defer.Deferred()
        stunrtp = StunHook(self)
        stunrtcp = StunHook(self.RTCP)
        dl = defer.DeferredList([rtpDef, rtcpDef])
        dl.addCallback(self.setStunnedAddress)
        stunrtp.discoverStun(rtpDef)
        stunrtcp.discoverStun(rtcpDef)

    def setStunnedAddress(self, results):
        ''' Handle results of the rtp/rtcp STUN. We have to check that 
            the results have the same IP and usable port numbers
        '''
        print "got STUN back!", results
        rtpres, rtcpres = results
        if rtpres[0] != defer.SUCCESS or rtcpres[0] != defer.SUCCESS:
            # barf out.
            print "uh oh, stun failed", results
        else:    
            code1, rtp = rtpres
            code2, rtcp = rtcpres
            if rtp[0] != rtcp[0]:
                print "stun gave different IPs for rtp and rtcp", results
            elif ((rtcp[1] % 2) != 1) or ((rtp[1] % 2) != 0):
                print "stun showed unusable rtp/rtcp ports", results
                # XXX close connection, try again, tell user
            else:
                # phew. working NAT
                print "discovered sane NAT for RTP/RTCP"
                self._extIP, self._extRTPPort = rtp
                d = self._stunCompleteDef 
                del self._stunCompleteDef 
                d.callback(rtp)

    def getSDP(self):
        from multicast.SDP import SimpleSDP
        self.getAudio()
        s = SimpleSDP()
        s.setPacketSize(160)
	addr = self.getVisibleAddress()
        print "addr = ", addr
        s.setServerIP(addr[0])
        s.setLocalPort(addr[1])
        fmts = self.infp.listFormats()
        if FMT_PCMU in fmts:
            s.addRtpMap('PCMU', 8000) # G711 ulaw
        if FMT_GSM in fmts:
            s.addRtpMap('GSM', 8000) # GSM 06.10
        if FMT_SPEEX in fmts:
            s.addRtpMap('speex', 8000, payload=110)
            #s.addRtpMap('speex', 16000, payload=111)
        if FMT_DVI4 in fmts:
            s.addRtpMap('DVI4', 8000)
            #s.addRtpMap('DVI4', 16000)
        return s

    def setFormat(self, rtpmap):
        for entry in rtpmap:        
            if entry == self.PT_pcmu:
                self.infp.setFormat(FMT_PCMU)
                break
            elif entry == self.PT_gsm:
                self.infp.setFormat(FMT_GSM)
                break
            else:
                print "couldn't set to %r"%entry
        else:
            raise ValueError, "no working formats"

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

    def getAudio(self):
        self.infp = getAudioDevice('rw')
        self.infp.close()
        self.outfp = self.infp

    def startSendingAndReceiving(self, dest, fp=None):
        self.dest = dest
        self.infp.reopen()
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
            self.sample = self.infp.read()
        except IOError: # stupid sound devices
            self.sample = None
            pass
        self.LC = LoopingCall(self.nextpacket)
        self.LC.start(0.020)
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
            # Don't care about the marker bit.
            PT = hdr[1]&127 
            fmt = None
            if PT == 0:
                fmt = FMT_PCMU
            elif PT == 3:
                fmt = FMT_GSM
            if fmt:
                try:
                    self.outfp.write(datagram[12:], fmt)
                except IOError:
                    pass
            elif PT in (13, 19):
                # comfort noise
                pass
            else:
                print "unexpected RTP PT %s len %d, HDR: %02x %02x"%(rtpPTDict.get(PT,str(PT)), len(datagram),hdr[0],hdr[1])

    def genSSRC(self):
        # Python-ish hack at RFC1889, Appendix A.6
        m = md5.new()
        m.update(str(time()))
        if hasattr(os, 'getuid'):
            m.update(str(os.getuid()))
            m.update(str(os.getgid()))
        m.update(str(socket.gethostname()))
        hex = m.hexdigest()
        nums = hex[:8], hex[8:16], hex[16:24], hex[24:]
        nums = [ long(x, 17) for x in nums ]
        ssrc = 0
        for n in nums: ssrc = ssrc ^ n
        ssrc = ssrc & (2**32 - 1)
        return ssrc

    def genInitTS(self):
        # Python-ish hack at RFC1889, Appendix A.6
        m = md5.new()
        m.update(str(self.genSSRC()))
        m.update(str(time()))
        hex = m.hexdigest()
        nums = hex[:8], hex[8:16], hex[16:24], hex[24:]
        nums = [ long(x, 16) for x in nums ]
        ts = 0
        for n in nums: ts = ts ^ n
        ts = ts & (2**32 - 1)
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
            if (self.packets - self.sent) %10 == 0:
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
                self.sample = self.infp.read()
        except IOError:
            pass
        
        if (self.sample is not None) and (len(self.sample) == 0):
            print "And we're done!"
            self.Done = 1


