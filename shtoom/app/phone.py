# Copyright (C) 2004 Anthony Baxter

# The Phone app.

from shtoom.app.interfaces import Application
from shtoom.app.base import BaseApplication
from twisted.internet import defer
from twisted.python import log
from shtoom.exceptions import CallFailed

from shtoom.audio import FMT_PCMU, FMT_GSM, FMT_SPEEX, FMT_DVI4
from shtoom.audio import getAudioDevice

class Phone(BaseApplication):
    __implements__ = ( Application, )

    def __init__(self, ui=None, audio=None):
        # Mapping from callcookies to rtp object
        self._rtp = {}
        # Mapping from callcookies to call objects
        self._calls = {}
        self._pendingRTP = {}
        self._audio = audio
        self._audioFormat = None
        self.ui = ui

    def boot(self, options=None):
        from shtoom.ui.select import findUserInterface

        from shtoom.opts import buildOptions
        if options is None:
            options = buildOptions(self)
        self.initOptions(options)

        if self.ui is None:
            self.ui = findUserInterface(self, self.getPref('ui'))
        BaseApplication.boot(self)

    def register(self):
        register_uri = self.getPref('register_uri')
        if register_uri is not None:
            self.sip.register()

    def start(self):
        "Start the application."
        from twisted.internet import reactor
        self.register()
        reactor.run()
        self.ui.resourceUsage()

    def getAuth(self, method, realm):
        self.ui.getString("Please enter user,passwd for %s at %s"%(method, realm))

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
        from shtoom.rtp import RTPProtocol
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
        if self._audio is None:
            audioPref = self.getPref('audio')
            audio_in = self.getPref('audio_infile')
            audio_out = self.getPref('audio_outfile')
            if audio_in and audio_out:
                aF = ( audio_in, audio_out )
            else:
                aF = None
            self._audio = getAudioDevice('rw', audioPref, aF)
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

    def startDTMF(self, cookie, digit):
        rtp = self._rtp[cookie]
        rtp.startDTMF(digit)

    def stopDTMF(self, cookie, digit):
        rtp = self._rtp[cookie]
        rtp.stopDTMF(digit)

    def statusMessage(self, message):
        self.ui.statusMessage(message)

    def debugMessage(self, message):
        self.ui.debugMessage(message)

    def appSpecificOptions(self, opts):
        import os.path

        from shtoom.Options import OptionGroup, StringOption, ChoiceOption
        app = OptionGroup('shtoom', 'Shtoom')
        app.addOption(ChoiceOption('ui','use UI for interface', choices=['qt','gnome','tk','text']))
        app.addOption(ChoiceOption('audio','use AUDIO for interface', choices=['oss', 'fast', 'port']))
        app.addOption(StringOption('audio_infile','read audio from this file'))
        app.addOption(StringOption('audio_outfile','write audio to this file'))
        opts.addGroup(app)
        opts.setOptsFile('.shtoomrc')

    def authCred(self, method, uri, realm='unknown', retry=False):
        "Place holder for now"
        user = self.getPref('register_authuser')
        passwd = self.getPref('register_authpasswd')
        if user is not None and passwd is not None and retry is False:
            return defer.succeed((self.getPref('register_authuser'), 
                                 self.getPref('register_authpasswd')))
        elif hasattr(self.ui, 'getAuth'):
            return self.ui.getAuth("Auth needed for %s %s, realm '%s'"%(method, uri, realm))
        else:
            return defer.fail(CallFailed("No auth available"))

