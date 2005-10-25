# Copyright (C) 2004 Anthony Baxter

# The Message app. Accepts all calls, plays a message, then hangs up.

from shtoom.app.interfaces import Application
from shtoom.app.base import BaseApplication
from twisted.internet import defer
from twisted.python import log
from twisted.protocols import sip as tpsip
from shtoom.exceptions import CallFailed
import sys, traceback
import shtoom.log

from shtoom.rtp.formats import PT_PCMU, PT_GSM, PT_SPEEX, PT_DVI4

from gettext import gettext as _

nteMap = { 0: '0',  1: '1',  2: '2',  3: '3',  4: '4',  5: '5',  6: '6',
           7: '7',  8: '8',  9: '9', 10: '*', 11: '#', 12: 'A', 13: 'B',
          14: 'C', 15: 'D', 16: 'flash' }

class DougApplication(BaseApplication):
    __implements__ = ( Application, )

    configFileName = '.dougrc'
    needLogging = True

    def __init__(self, voiceapp, ui=None, audio=None):
        # Mapping from callcookies to rtp object
        self._rtp = {}
        # Mapping from callcookies to call objects
        self._calls = {}
        # Mapping from callcookies to voiceapp instances
        self._voiceapps = {}
        self._voiceappClass = voiceapp
        self._voiceappArgs = {}

    def boot(self, options=None, args=None):
        from shtoom.opts import buildOptions
        if options is None:
            options = buildOptions(self)
        self.initOptions(options, args)
        if not self.needLogging:
            # Need to leave things alone when under trial
            pass
        elif not self.getPref('logfile'):
            print "logging to stdout"
            shtoom.log.startLogging(sys.stdout)
        else:
            file = open(self.getPref('logfile'), 'aU')
            #print "logging to file", file
            shtoom.log.startLogging(file)
        BaseApplication.boot(self)

    def start(self):
        "Start the application."
        from twisted.internet import reactor
        vargs = self.getPref('dougargs')
        if vargs:
            kwargs = [x.split('=') for x in vargs.split(',') ]
            self._voiceappArgs = dict(kwargs)
            for k in self._voiceappArgs:
                if isinstance(k, unicode):
                    v = self._voiceappArgs[k]
                    del self._voiceappArgs[k]
                    self._voiceappArgs[k.encode('ascii')] = v

        register_uri = self.getPref('register_uri')
        if register_uri is not None:
            d = self.sip.register()
            d.addCallback(log.err).addErrback(log.err)
        # Don't start reactor if it's already running. Ugh.
        if not hasattr(reactor,'running') or not reactor.running:
            reactor.run()

    def initVoiceapp(self, callcookie, args=None):
        if args is None: 
            args = {}
        log.msg("creating voiceapp %r with start args %r"%(self._voiceappClass,args), system='doug')
        d = defer.Deferred()
        d.addCallbacks(lambda x: self.acceptResults(callcookie,x),
                       lambda x: self.acceptErrors(callcookie,x))
        try:
            v = self._voiceappClass(d, self, callcookie, **self._voiceappArgs)
            v.va_start(args)
        except:
            ee,ev,et = sys.exc_info()
            log.err("voiceapp init failed: %s, %s, %s"%(ee, ev, traceback.extract_tb(et)))
            v = None
        if v:
            log.msg("new voiceapp %r"%(v), system='doug')
            self._voiceapps[callcookie] = v

    def bong(self, failure):
        print failure.value
        log.err(failure)
        return failure

    def listVoiceapps(self):
        return self._voiceapps.values()

    def acceptResults(self, callcookie, results):
        log.msg("callcookie %s ended with result %s"%(callcookie, results),
                                                                system='doug')
        self.dropCall(callcookie)

    def acceptErrors(self, callcookie, error):
        log.msg("callcookie %s ended with ERROR %r"%(callcookie, error),
                                                                system='doug')
        self.dropCall(callcookie)

    def startVoiceApp(self, **args):
        "Start a voiceapp (without an inbound leg)"
        cookie = self.getCookie()
        self.initVoiceapp(cookie, args)
        self._voiceapps[cookie].va_callstart(None, args)

    def acceptCall(self, call):
        from shtoom.doug.leg import Leg
        log.msg("acceptCall dialog is %r"%(call.dialog), system='doug')
        calltype = call.dialog.getDirection()
        if call.cookie is None:
            cookie = self.getCookie()
        else:
            cookie = call.cookie
        self._calls[cookie] = call
        d = self._createRTP(cookie,
                            call.getLocalSIPAddress()[0],
                            call.getSTUNState())
        if calltype == 'outbound':
            # Outbound call, trigger the callback immediately
            d.addCallback(lambda x: cookie)
        elif calltype == 'inbound':
            # Otherwise we chain callbacks
            self.initVoiceapp(cookie)
            d.addErrback(lambda x: self.rejectedCall(cookie, x))
            ad = defer.Deferred()
            inbound = Leg(cookie, call.dialog)
            inbound.incomingCall(ad)
            self._voiceapps[cookie].va_callstart(inbound)
            d.addCallback(lambda x, ad=ad: ad)
        else:
            raise ValueError, "unknown call type %s"%(calltype)
        d.addErrback(self.bong)
        return d

    def rejectedCall(self, callcookie, reason):
        del self._calls[callcookie]
        del self._voiceapps[callcookie]
        return reason

    def _createRTP(self, cookie, fromIP, withSTUN):
        from shtoom.rtp.protocol import RTPProtocol
        rtp = RTPProtocol(self, cookie)
        self._rtp[cookie] = rtp
        d = rtp.createRTPSocket(fromIP,withSTUN)
        return d

    def selectDefaultFormat(self, callcookie, sdp):
        md = sdp.getMediaDescription('audio')
        rtpmap = md.rtpmap
        v = self._voiceapps.get(callcookie)
        ptlist = [ x[1] for x in  rtpmap.values() ]
        v.va_selectDefaultFormat(ptlist, callcookie=callcookie)

    def getSDP(self, callcookie, othersdp=None):
        rtp = self._rtp[callcookie]
        sdp = rtp.getSDP(othersdp)
        return sdp

    def startCall(self, callcookie, remoteSDP, cb):
        # create an inboundLeg
        from shtoom.doug.leg import Leg
        md = remoteSDP.getMediaDescription('audio')
        ipaddr = md.ipaddr or remoteSDP.ipaddr
        remoteAddr = (ipaddr, md.port)
        self._rtp[callcookie].start(remoteAddr)
        call = self._calls[callcookie]
        if call.dialog.getDirection() == "inbound":
            self._voiceapps[callcookie].va_callanswered()
        log.msg("call %s connected"%callcookie, system='doug')
        cb(callcookie)

    def endCall(self, callcookie, reason=''):
        log.msg("call %s disconnected"%callcookie, reason, system='doug')
        if self._rtp.get(callcookie):
            rtp = self._rtp[callcookie]
            rtp.stopSendingAndReceiving()
            del self._rtp[callcookie]
        if self._calls.get(callcookie):
            del self._calls[callcookie]
        if self._voiceapps.get(callcookie):
            self._voiceapps[callcookie].va_abort()
            del self._voiceapps[callcookie]

    def incomingRTP(self, callcookie, packet):
        from shtoom.rtp.formats import PT_NTE
        v = self._voiceapps[callcookie]
        if packet.header.ct is PT_NTE:
            data = packet.data
            key = ord(data[0])
            start = (ord(data[1]) & 128) and True or False
            if start:
                #print "start inbound dtmf", key
                v.va_startDTMFevent(nteMap[key], callcookie)
            else:
                #print "stop inbound dtmf", key
                v.va_stopDTMFevent(nteMap[key], callcookie)
            return
        try:
            self._voiceapps[callcookie].va_incomingRTP(packet, callcookie)
        except IOError:
            pass

    def outgoingRTP(self, cookie, sample):
        #print "outgoingRTP", cookie, self._rtp.keys()
        rtp = self._rtp.get(cookie)
        if rtp:
            rtp.handle_media_sample(sample)

    def placeCall(self, cookie, nleg, sipURL, fromURI=None):
        ncookie = self.getCookie()
        nleg.setCookie(ncookie)
        self._voiceapps[cookie].setLeg(nleg, ncookie)
        self._voiceapps[ncookie] = self._voiceapps[cookie]
        log.msg("connecting %s to %s"%(ncookie, cookie), system='doug')
        d = self.sip.placeCall(sipURL, fromURI, cookie=ncookie)
        d.addCallbacks(
            lambda x: self.outboundCallConnected(nleg, cookie, x),
            lambda x: self.outboundCallFailed(nleg, cookie, ncookie, x)
                                                    ).addErrback(log.err)
        return d

    def outboundCallConnected(self, leg, voiceappCookie, outboundCookie):
        log.msg("outbound connected %r->%r"%(voiceappCookie, outboundCookie),
                                                    system='doug')
        call = self._calls[outboundCookie]
        leg.setDialog(call.dialog)
        leg.outgoingCall()
        self._voiceapps[voiceappCookie].va_callanswered(leg)

    def outboundCallFailed(self, leg, voiceappCookie, outboundCookie, exc):
        from shtoom.doug.leg import Leg
        log.msg("outbound failed %r->%r"%(voiceappCookie, outboundCookie),
                                                    system='doug')
        call = self._calls[outboundCookie]
        leg.setDialog(call.dialog)
        leg.outgoingCall()
        self._voiceapps[voiceappCookie].va_callrejected(leg)

    def dropCall(self, cookie):
        log.msg("dropCall %r"%(cookie), system='doug')
        if cookie in self._calls:
            return self._calls.get(cookie).dropCall()
        elif cookie in self._voiceapps:
                return #self._voiceapps.get(cookie).va_abort()
        else:
            log.err("Couldn't find cookie %s, have %r, %r"%(cookie,
                                self._calls.keys(), self._voiceapps.keys(), ))
            return

    def statusMessage(self, message):
        log.msg("STATUS: "+message, system='doug')

    def debugMessage(self, message):
        log.msg(message, system='doug')

    def appSpecificOptions(self, opts):
        import os.path

        from shtoom.Options import OptionGroup, StringOption, ChoiceOption
        app = OptionGroup('doug', 'doug')
        app.add(StringOption('logfile','log to this file'))
        app.add(StringOption('dougargs',
                                'pass these arguments to the voiceapp'))
        opts.add(app)
        if self.configFileName is not None:
            opts.setOptsFile(self.configFileName)

    def authCred(self, method, uri, realm='unknown', retry=False):
        "Place holder for now"
        user = self.getPref('register_authuser')
        passwd = self.getPref('register_authpasswd')
        if user is not None and passwd is not None and retry is False:
            return defer.succeed((self.getPref('register_authuser'),
                                 self.getPref('register_authpasswd')))
        else:
            raise defer.fail(CallFailed("No auth available"))

    def startDTMF(self, cookie, digit):
        #print "app.startDTMF", cookie, digit
        rtp = self._rtp.get(cookie)
        if rtp:
            rtp.startDTMF(digit)

    def stopDTMF(self, cookie, digit):
        #print "app.stopDTMF", cookie, digit
        rtp = self._rtp.get(cookie)
        if rtp:
            rtp.stopDTMF(digit)

    def notifyEvent(self, methodName, *args, **kw):
        pass

    def ringBack(self):
        pass

    def ipcCommand(self, command, args):
        pass
