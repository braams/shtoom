# Copyright (C) 2004 Anthony Baxter

# The Message app. Accepts all calls, plays a message, then hangs up.

from shtoom.app.interfaces import Application
from shtoom.app.base import BaseApplication
from twisted.internet import defer
from twisted.python import log
import sys

from shtoom.audio import FMT_PCMU, FMT_GSM, FMT_SPEEX, FMT_DVI4
from shtoom.audio.fileaudio import getFileAudio

class Message(BaseApplication):
    __implements__ = ( Application, )

    def __init__(self, ui=None, audio=None):
        # Mapping from callcookies to rtp object
        self._rtp = {}
        # Mapping from callcookies to call objects
        self._calls = {}
        self._pendingRTP = {}
        self._audios = {}
        self._audioFormats = {}

    def boot(self, options=None):
        from shtoom.opts import buildOptions
        if options is None:
            options = buildOptions(self)
        self.initOptions(options)
        log.startLogging(sys.stdout)
        BaseApplication.boot(self)

    def start(self):
        "Start the application."
        from twisted.internet import reactor
        register_uri = self.getPref('register_uri')
        if register_uri is not None:
            d = self.sip.register()
            d.addCallback(log.err).addErrback(log.err)
        reactor.run()

    def acceptCall(self, call, **calldesc):
        print "acceptCall for %r"%calldesc

        calltype = calldesc.get('calltype')
        d = defer.Deferred()
        cookie = self.getCookie()
        self.openAudioDevice(cookie)
        d.addCallback(lambda x: self._createRTP(cookie,
                                                calldesc['fromIP'],
                                                calldesc['withSTUN']))
        self._calls[cookie] = call
        if calltype == 'outbound':
            # Outbound call, trigger the callback immediately
            d.callback('')
        elif calltype == 'inbound':
            # Otherwise we chain callbacks
            log.msg("accepting incoming call from %s"%calldesc['desc'])
            d.callback('ok')
        else:
            raise ValueError, "unknown call type %s"%(calltype)
        return cookie, d

    def _createRTP(self, cookie, fromIP, withSTUN):
        from shtoom.rtp import RTPProtocol
        rtp = RTPProtocol(self, cookie)
        self._rtp[cookie] = rtp
        d = rtp.createRTPSocket(fromIP,withSTUN)
        return d

    def openAudioDevice(self, callcookie):
        audio_in = self.getPref('audio_infile')
        self._audios[callcookie] = getFileAudio(audio_in, '/dev/null')

    def selectFormat(self, callcookie, rtpmap):
        rtp =  self._rtp[callcookie]
        audio = self._audios.get(callcookie)
        for entry,desc in rtpmap:
            if entry == rtp.PT_pcmu:
                audio.selectFormat(FMT_PCMU)
                self._audioFormats[callcookie] = entry
                break
            elif entry == rtp.PT_gsm:
                audio.selectFormat(FMT_GSM)
                self._audioFormats[callcookie] = entry
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
        fmts = self._audios[callcookie].listFormats()
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
        self._rtp[callcookie].startSendingAndReceiving(remoteAddr)
        log.msg("call %s connected"%callcookie)
        cb(callcookie)

    def endCall(self, callcookie, reason=''):
        rtp = self._rtp[callcookie]
        rtp.stopSendingAndReceiving()
        del self._rtp[callcookie]
        if self._calls.get(callcookie):
            del self._calls[callcookie]
        self.closeAudioDevice(callcookie)
        log.msg("call %s disconnected"%callcookie, reason)

    def closeAudioDevice(self, callcookie):
        self._audios[callcookie].close()
        del self._audios[callcookie]

    def receiveRTP(self, callcookie, payloadType, payloadData):
        fmt = None
        if payloadType == 0:
            fmt = FMT_PCMU
        elif payloadType == 3:
            fmt = FMT_GSM
        if fmt:
            try:
                self._audios[callcookie].write(payloadData, fmt)
            except IOError:
                pass
        elif payloadType in (13, 19):
            # comfort noise
            pass
        else:
            print "unexpected RTP PT %s len %d"%(rtpPTDict.get(payloadType,str(payloadType)), len(datagram))

    def giveRTP(self, callcookie):
        # Check that callcookie is the active call!
        return self._audioFormats[callcookie], self._audios[callcookie].read()

    def placeCall(self, sipURL):
        return self.sip.placeCall(sipURL)

    def dropCall(self, cookie):
        call = self._calls[cookie]
        call.dropCall()
        if self._calls.get(cookie):
            del self._calls[cookie]

    def statusMessage(self, message):
        log.msg("STATUS: "+message)

    def debugMessage(self, message):
        log.msg(message)

    def appSpecificOptions(self, opts):
        import os.path

        from shtoom.Options import OptionGroup, StringOption, ChoiceOption
        app = OptionGroup('shtoom', 'Shtoom')
        app.addOption(StringOption('audio_infile','read audio from this file'))
        app.addOption(StringOption('audio_outfile','write audio to this file'))
        opts.addGroup(app)
        opts.setOptsFile('.shmessagerc')

    def authCred(self, method, uri, realm='unknown', retry=False):
        "Place holder for now"
        user = self.getPref('register_authuser')
        passwd = self.getPref('register_authpasswd')
        if user is not None and passwd is not None and retry is False:
            return defer.succeed((self.getPref('register_authuser'), 
                                 self.getPref('register_authpasswd')))
        else:
            raise CallFailed, "No auth available"
