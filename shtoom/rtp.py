# Copyright (C) 2004 Anthony Baxter

# Feed it hostname, port, and an audio file (in 8bit ulaw - sox -t ul)
# Or skip the audio file and it'll read from the microphone
# See also rtprecv.py for something that listens to a port and dumps it to
# the audio device
#
# $Id: rtp.py,v 1.38 2004/03/06 10:17:56 anthony Exp $
#

import signal, struct, random, os, md5, socket
from time import sleep, time

from twisted.internet import reactor, defer
from twisted.internet.protocol import ConnectedDatagramProtocol
from twisted.internet.task import LoopingCall
from twisted.python import log

from shtoom.multicast.SDP import rtpPTDict


class RTPProtocol(ConnectedDatagramProtocol):
    """Implementation of the RTP protocol.

    Also manages a RTCP instance.
    """

    _stunAttempts = 0

    _cbDone = None
    PT_pcmu = rtpPTDict[('PCMU', 8000, 1)]
    PT_gsm = rtpPTDict[('GSM', 8000, 1)]

    def __init__(self, app, cookie, *args, **kwargs):
        self.app = app
        self.cookie = cookie
        #DatagramProtocol.__init__(self, *args, **kwargs)

    def createRTPSocket(self, locIP, needSTUN=False):
        """ Start listening on UDP ports for RTP and RTCP.

            Returns a Deferred, which is triggered when the sockets are
            connected, and any STUN has been completed. The deferred
            callback will be passed (extIP, extPort). (The port is the RTP
            port.) We don't guarantee a working RTCP port, just RTP.
        """
        self.needSTUN=needSTUN
        d = defer.Deferred()
        self._socketCompleteDef = d
        self._socketCreationAttempt(locIP)
        return d

    def _socketCreationAttempt(self, locIP=None):
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
        if self.needSTUN is False:
            # The pain can stop right here
            self._extRTPPort = rtpPort
            self._extIP = locIP
            d = self._socketCompleteDef
            del self._socketCompleteDef
            d.callback((locIP, rtpPort))
        else:
            # If the NAT is doing port translation as well, we will just
            # have to try STUN and hope that the RTP/RTCP ports are on
            # adjacent port numbers. Please, someone make the pain stop.
            self.discoverStun()

    def getVisibleAddress(self):
        ''' returns the local IP address used for RTP (as visible from the
            outside world if STUN applies) as ( 'w.x.y.z', rtpPort)
        '''
        return (self._extIP, self._extRTPPort)

    def discoverStun(self):
        ''' Uses STUN to discover the external address for the RTP/RTCP
            ports. deferred is a Deferred to be triggered when STUN is
            complete.
        '''
        # See above comment about port translation.
        # We have to do STUN for both RTP and RTCP, and hope we get a sane
        # answer.
        from shtoom.stun import StunHook
        rtpDef = defer.Deferred()
        rtcpDef = defer.Deferred()
        stunrtp = StunHook(self)
        stunrtcp = StunHook(self.RTCP)
        dl = defer.DeferredList([rtpDef, rtcpDef])
        dl.addCallback(self.setStunnedAddress).addErrback(log.err)
        stunrtp.discoverStun(rtpDef)
        stunrtcp.discoverStun(rtcpDef)

    def setStunnedAddress(self, results):
        ''' Handle results of the rtp/rtcp STUN. We have to check that
            the results have the same IP and usable port numbers
        '''
        log.msg("got STUN back! %r"%(results))
        rtpres, rtcpres = results
        if rtpres[0] != defer.SUCCESS or rtcpres[0] != defer.SUCCESS:
            # barf out.
            log.msg("uh oh, stun failed %r"%(results))
        else:
            code1, rtp = rtpres
            code2, rtcp = rtcpres
            if rtp[0] != rtcp[0]:
                print "stun gave different IPs for rtp and rtcp", results
            # We _should_ try and see if we have working rtp and rtcp, but
            # this seems almost impossible with most firewalls. So just try
            # to get a working rtp port (an even port number is required).
            elif ((rtp[1] % 2) != 0):
                log.msg("stun showed unusable rtp/rtcp ports %r, retry number %d"%(results, self._stunAttempts))
                # XXX close connection, try again, tell user
                if self._stunAttempts > 8:
                    # XXX
                    print "Giving up. Made %d attempts to get a working port"%(
                        self._stunAttempts)
                self._stunAttempts += 1
                self.rtpListener.stopListening()
                self.rtcpListener.stopListening()
                self._socketCreationAttempt()
            else:
                # phew. working NAT
                log.msg("discovered sane NAT for RTP/RTCP")
                self._extIP, self._extRTPPort = rtp
                self._stunAttempts = 0
                d = self._socketCompleteDef
                del self._socketCompleteDef
                d.callback(rtp)

    def whenDone(self, cbDone):
        self._cbDone = cbDone

    def stopSendingAndReceiving(self):
        self.Done = 1
        self.rtpListener.stopListening()
        self.rtcpListener.stopListening()

    def startSendingAndReceiving(self, dest, fp=None):
        reactor.connectUDP(dest[0], dest[1], self)
        self.dest = dest
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
            self.sample = self.app.giveRTP(self.cookie)
        except IOError: # stupid sound devices
            self.sample = None
            pass
        self.LC = LoopingCall(self.nextpacket)
        self.LC.start(0.020)
        # Now send a single CN packet to seed any firewalls that might
        # need an outbound packet to let the inbound back.
        # PT 13 is CN.
        log.msg("sending comfort noise to seed firewall")
        hdr = struct.pack('!BBHII', 0x80, 13, self.seq, self.ts, self.ssrc)
        self.transport.write(hdr+chr(0))

    def reactorWakeUp(self, n, f, reactor=reactor):
        reactor.wakeUp()

    def datagramReceived(self, datagram, addr, unpack=struct.unpack):
        hdr = struct.unpack('!BBHII', datagram[:12])
        # Don't care about the marker bit.
        PT = hdr[1]&127
        data = datagram[12:]
        self.app.receiveRTP(self.cookie, PT, data)

    def connectionRefused(self):
        log.err("RTP got a connection refused, ending call")
        self.Done = True
        self.app.dropCall(self.cookie)

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
        tt = time()
        if self.Done:
            self.LC.stop()
            if self._cbDone:
                self._cbDone()
            return
        self.packets += 1
        if self.sample is not None:
            fmt, sample = self.sample
            self.sent += 1
            hdr = pack('!BBHII', 0x80, fmt, self.seq, self.ts, self.ssrc)
            self.transport.write(hdr+sample)
            self.sample = None
        else:
            if (self.packets - self.sent) %10 == 0:
                print "skipping audio, %s/%s sent"%(self.sent, self.packets)
        self.seq += 1
        self.ts += 160
        try:
            self.sample = self.app.giveRTP(self.cookie)
        except IOError:
            pass

        if 0 and (self.sample is not None) and (len(self.sample) == 0):
            print "And we're done!"
            self.Done = 1
        tt = (time() - tt) * 1000
        #print "timing: %.3fms"% ( tt )

    def startDTMF(self, digit):
        print "start sending %s"%digit

    def stopDTMF(self, digit):
        print "stop sending %s"%digit

