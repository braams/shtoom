# Copyright (C) 2004 Anthony Baxter
# This file is necessary to make this directory a package

# The Phone app.

from interfaces import IPhoneApplication
from base import BaseApplication
from twisted.internet import reactor, defer

from shtoom.audio import FMT_PCMU, FMT_GSM, FMT_SPEEX, FMT_DVI4
from shtoom.audio import getAudioDevice
from shtoom.rtp import RTPProtocol

class Phone(BaseApplication):
    __implements__ = ( IPhoneApplication, )

    def __init__(self):
        from shtoom.ui.select import findUserInterface
        BaseApplication.__init__(self)
        self.ui = findUserInterface(self)
        # Mapping from callcookies to rtp object
        self._rtp = {}
        # Mapping from callcookies to call objects
        self._calls = {}

        self._pendingRTP = {}
        self._audio = None
        self._audioFormat = None

    def start(self):
        "Start the application."
        reactor.run()
        self.ui.resourceUsage()

    def acceptCall(self, call, **calldesc):
        print "acceptCall for %r"%calldesc

        if self._audio is None:
            self.openAudioDevice()
        calltype = calldesc.get('calltype')
        d = defer.Deferred()
        d.addCallback(lambda x: self._createRTP(cookie,
                                                calldesc['fromIP'],
                                                calldesc['withSTUN']))
        cookie = self.getCookie()
        self._calls[cookie] = call
        if calltype == 'outbound':
            # Outbound call, trigger the callback immediately
            d.callback('')
        elif calltype == 'inbound':
            # Otherwise we chain callbacks
            self.ui.incomingCall(calldesc['desc'], cookie, d)
        else:
            raise ValueError, "unknown call type %s"%(calltype)
        return cookie, d

    def _createRTP(self, cookie, fromIP, withSTUN):
        rtp = RTPProtocol(self, cookie)
        self._rtp[cookie] = rtp
        d = rtp.createRTPSocket(fromIP,withSTUN)
        return d

    def selectFormat(self, callcookie, rtpmap):
        rtp =  self._rtp[callcookie]
        for entry,desc in rtpmap:
            if entry == rtp.PT_pcmu:
                self._audio.selectFormat(FMT_PCMU)
                self._audioFormat = entry
                break
            elif entry == rtp.PT_gsm:
                self._audio.selectFormat(FMT_GSM)
                self._audioFormat = entry
                break
            else:
                raise ValueError, "couldn't set to %r"%entry
        else:
            raise ValueError, "no working formats"

    def getSDP(self, callcookie):
        from shtoom.multicast.SDP import SimpleSDP
        rtp =  self._rtp[callcookie]
        s = SimpleSDP()
        s.setPacketSize(160)
        addr = rtp.getVisibleAddress()
        s.setServerIP(addr[0])
        s.setLocalPort(addr[1])
        fmts = self._audio.listFormats()
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

    def startCall(self, callcookie, remoteAddr, cb):
        self._audio.reopen()
        self._rtp[callcookie].startSendingAndReceiving(remoteAddr)
        self.ui.callConnected(callcookie)
        cb(callcookie)

    def endCall(self, callcookie, reason=''):
        rtp = self._rtp[callcookie]
        rtp.stopSendingAndReceiving()
        del self._rtp[callcookie]
        if self._calls.get(callcookie):
            del self._calls[callcookie]
        self.closeAudioDevice()
        self.ui.callDisconnected(callcookie, reason)

    def openAudioDevice(self):
        self._audio = getAudioDevice('rw')
        self._audio.close()

    def closeAudioDevice(self):
        self._audio.close()
        self._audio = None

    def receiveRTP(self, callcookie, payloadType, payloadData):
        fmt = None
        if payloadType == 0:
            fmt = FMT_PCMU
        elif payloadType == 3:
            fmt = FMT_GSM
        if fmt:
            try:
                self._audio.write(payloadData, fmt)
            except IOError:
                pass
        elif payloadType in (13, 19):
            # comfort noise
            pass
        else:
            print "unexpected RTP PT %s len %d"%(rtpPTDict.get(payloadType,str(payloadType)), len(datagram))


    def giveRTP(self, callcookie):
        # Check that callcookie is the active call!
        return self._audioFormat, self._audio.read()

    def placeCall(self, sipURL):
        return self.sip.placeCall(sipURL)

    def dropCall(self, cookie):
        call = self._calls[cookie]
        call.dropCall()
        if self._calls.get(cookie):
            del self._calls[cookie]

    def startDTMF(self, callid, digit):
        rtp = self._rtp[callid]

    def stopDTMF(self, callid, digit):
        rtp = self._rtp[callid]

    def statusMessage(self, message):
        self.ui.statusMessage(message)

    def debugMessage(self, message):
        self.ui.debugMessage(message)
