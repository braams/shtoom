# Copyright (C) 2004 Anthony Baxter

# The Message app. Accepts all calls, plays a message, then hangs up.

from shtoom.app.interfaces import Application
from shtoom.app.base import BaseApplication
from twisted.internet import defer
from twisted.python import log
from twisted.protocols import sip as tpsip
from shtoom.exceptions import CallFailed
from shtoom.multicast.SDP import rtpPTDict
import sys, traceback

from shtoom.audio import FMT_PCMU, FMT_GSM, FMT_SPEEX, FMT_DVI4
from shtoom.audio.fileaudio import getFileAudio

nteMap = { 0: '0', 1: '1', 2:'2', 3:'3', 4:'4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9',
           10: '*', 11: '#', 12: 'A', 13: 'B', 14:'C', 15:'D', 16:'flash' }

class DougApplication(BaseApplication):
    __implements__ = ( Application, )

    def __init__(self, voiceapp, ui=None, audio=None):
        # Mapping from callcookies to rtp object
        self._rtp = {}
        # Mapping from callcookies to call objects
        self._calls = {}
        # Mapping from callcookies to voiceapp instances
        self._voiceapps = {}
        self._voiceappClass = voiceapp

    def boot(self, options=None):
        from shtoom.opts import buildOptions
        if options is None:
            options = buildOptions(self)
        self.initOptions(options)
        if not self.getPref('logfile'):
            log.startLogging(sys.stdout)
        else:
            log.startLogging(open(self.getPref('logfile'), 'aU'))
        BaseApplication.boot(self)

    def start(self):
        "Start the application."
        from twisted.internet import reactor
        register_uri = self.getPref('register_uri')
        if register_uri is not None:
            d = self.sip.register()
            d.addCallback(log.err).addErrback(log.err)
        reactor.run()

    def initVoiceapp(self, callcookie):
        print "creating voiceapp", self._voiceappClass
        d = defer.Deferred()
        d.addCallbacks(lambda x: self.acceptResults(callcookie,x), 
                       lambda x: self.acceptErrors(callcookie,x))
        try:
            v = self._voiceappClass(d)
            v.va_start()
        except:
            ee,ev,et = sys.exc_info() 
            print "voiceapp error", ee, ev, traceback.extract_tb(et)
            v = None
        if v:
            print "new voiceapp", v
            self._voiceapps[callcookie] = v

    def acceptResults(self, callcookie, results):
        print "callcookie %s ended with result %s"%(callcookie, results)
        self.dropCall(callcookie)

    def acceptErrors(self, callcookie, error):
        print "callcookie %s ended with ERROR %r"%(callcookie, error)
        self.dropCall(callcookie)

    def acceptCall(self, call, **calldesc):
        from shtoom.doug.leg import Leg
        print "acceptCall for %r"%calldesc

        print "dialog is", calldesc.get('dialog')
        calltype = calldesc.get('calltype')
        d = defer.Deferred()
        cookie = self.getCookie()
        self._calls[cookie] = call
        self.initVoiceapp(cookie)
        d.addCallback(lambda x: self._createRTP(cookie,
                                                calldesc['localIP'],
                                                calldesc['withSTUN']))
        if calltype == 'outbound':
            # Outbound call, trigger the callback immediately
            d.callback(cookie)
        elif calltype == 'inbound':
            # Otherwise we chain callbacks
            log.msg("starting incoming call from %s"%calldesc['desc'])
            d.addErrback(lambda x: self.rejectedCall(cookie, x))
            inbound = Leg(cookie, calldesc['dialog'])
            inbound.incomingCall(d)
            self._voiceapps[cookie].va_callstart(inbound)
        else:
            raise ValueError, "unknown call type %s"%(calltype)
        return d

    def rejectedCall(self, callcookie, reason):
        print "rejectedCall", callcookie, reason
        del self._calls[callcookie]
        del self._voiceapps[callcookie] 
        return reason

    def _createRTP(self, cookie, fromIP, withSTUN):
        from shtoom.rtp import RTPProtocol
        rtp = RTPProtocol(self, cookie)
        self._rtp[cookie] = rtp
        d = rtp.createRTPSocket(fromIP,withSTUN)
        return d

    def selectFormat(self, callcookie, rtpmap):
        print "RTP", rtpmap
        rtp =  self._rtp[callcookie]
        v = self._voiceapps.get(callcookie)
        for entry,desc in rtpmap:
            if entry == rtp.PT_pcmu:
                v.va_selectFormat(FMT_PCMU, entry)
                break
            elif entry == rtp.PT_gsm:
                v.va_selectFormat(FMT_GSM, entry)
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
        fmts = self._voiceapps[callcookie].va_listFormats()
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
        s.addRtpMap('telephone-event', 8000, payload=101)
        return s

    def startCall(self, callcookie, remoteAddr, cb):
        # create an inboundLeg
        from shtoom.doug.leg import Leg
        self._rtp[callcookie].startSendingAndReceiving(remoteAddr)
        self._voiceapps[callcookie].va_callanswered()
        log.msg("call %s connected"%callcookie)
        cb(callcookie)

    def endCall(self, callcookie, reason=''):
        log.msg("call %s disconnected"%callcookie, reason)
        if self._rtp.get(callcookie):
            rtp = self._rtp[callcookie]
            rtp.stopSendingAndReceiving()
            del self._rtp[callcookie]
        if self._calls.get(callcookie):
            del self._calls[callcookie]
        if self._voiceapps.get(callcookie):
            self._voiceapps[callcookie].va_abort()
            del self._voiceapps[callcookie]

    def receiveRTP(self, callcookie, payloadType, payloadData):
        # Yuk. If we're answering, the other end sets the PT!
        # XXX tofix!
        v = self._voiceapps[callcookie]
        if payloadType == 101:
            key = ord(payloadData[0])
            start = (ord(payloadData[1]) & 128) and True or False
            print "got dtmf", key, start
            if start:
                v.va_startDTMFevent(nteMap[key])
            else:
                v.va_stopDTMFevent(nteMap[key])
            return
        fmt = None
        if payloadType == 0:
            fmt = FMT_PCMU
        elif payloadType == 3:
            fmt = FMT_GSM
        if fmt:
            try:
                self._voiceapps[callcookie].va_receiveRTP(fmt,payloadData)
            except IOError:
                pass
        elif payloadType in (13, 19):
            # comfort noise
            pass
        else:
            print "unexpected RTP PT %s len %d"%((payloadType,str(payloadType)), len(payloadData))

    def giveRTP(self, callcookie):
        v = self._voiceapps[callcookie]
        fmt, data = v.va_giveRTP()
        return fmt, data

    def placeCall(self, sipURL):
        return self.sip.placeCall(sipURL)

    def dropCall(self, cookie):
        call = self._calls.get(cookie)
        if not call:
            log.err("Couldn't find cookie %s, have %r, %r"%(cookie, self._calls.keys(), self._voiceapps.keys(), ))
            return
        call.dropCall()

    def statusMessage(self, message):
        log.msg("STATUS: "+message)

    def debugMessage(self, message):
        log.msg(message)

    def appSpecificOptions(self, opts):
        import os.path

        from shtoom.Options import OptionGroup, StringOption, ChoiceOption
        app = OptionGroup('doug', 'doug')
        app.addOption(StringOption('logfile','log to this file'))
        opts.addGroup(app)
        opts.setOptsFile('.dougrc')

    def authCred(self, method, uri, realm='unknown', retry=False):
        "Place holder for now"
        user = self.getPref('register_authuser')
        passwd = self.getPref('register_authpasswd')
        if user is not None and passwd is not None and retry is False:
            return defer.succeed((self.getPref('register_authuser'),
                                 self.getPref('register_authpasswd')))
        else:
            raise defer.fail(CallFailed("No auth available"))
