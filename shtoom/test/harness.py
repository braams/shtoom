#!/usr/bin/env python

from twisted.internet import defer, stdio
from twisted.protocols import basic
from twisted.python import log
from shtoom.exceptions import CallRejected, CallFailed, HostNotKnown

from time import time

class TestCall:
    "A fake Call object"
    def __init__(self, sip, uri=None):
        self.sip = sip
        self.uri = uri

    def startCall(self):
        self.d = defer.Deferred()
        return self.d

    def getLocalSIPAddress(self):
        return ( '127.0.0.1', 5060)

    def getSTUNState(self):
        return False

    def startFakeInbound(self):
        from shtoom.sip import Dialog
        self.dialog = Dialog(caller=self.uri)
        self.dialog.setDirection(inbound=True)
        d = self.sip.app.acceptCall(call=self)
        d.addCallbacks(self._cb_incomingCall, self.failedIncoming).addErrback(log.err)

    def startFakeOutbound(self, uri):
        from shtoom.sip import Dialog
        self.dialog = Dialog()
        self.dialog.setDirection(outbound=True)
        if 'auth' in uri:
            # Any test calls to a URI containing the string 'auth'
            # trigger an auth dialog
            d = self.sip.app.authCred('INVITE', uri, realm='fake.realm.here')
            d.addCallback(self._cb_startFakeOutboundWithAuth, uri)
        if 'reject' in uri:
            # Any test calls to a URI containing the string 'reject'
            # will fail. 
            d, self.d = self.d, None
            d.errback(CallFailed('rejected call'))
        else:
            d = self.sip.app.acceptCall(call=self)
            d.addCallbacks(self._cb_incomingCall,
                           self.failedIncoming).addErrback(log.err)

    def _cb_startFakeOutboundWithAuth(self, auth, uri):
        print "got auth", auth
        d = self.sip.app.acceptCall(call=self)
        d.addCallbacks(self._cb_incomingCall,
                       self.failedIncoming).addErrback(log.err)

    def _cb_incomingCall(self, response):
        from shtoom.exceptions import CallFailed
        if isinstance(response, CallFailed):
            return self.rejectedFakeCall(response)
        else:
            return self.acceptedFakeCall(response)

    def failedIncoming(self, failure):
        print "failed, got %r"%(failure,)
        d, self.d = self.d, None
        d.errback(failure)
        return failure

    def acceptedFakeCall(self, cookie):
        print "accepted, got %r"%(cookie,)
        from shtoom.rtp.formats import PT_PCMU, SDPGenerator
        from shtoom.exceptions import CallRejected
        self.cookie = cookie
        self.sip.app.selectDefaultFormat(self.cookie, sdp=None,fmts=[PT_PCMU,])
        sdp = SDPGenerator().getSDP(self)
        d, self.d = self.d, None
        self.sip.app.startCall(self.cookie, sdp, d.callback)

    def rejectedFakeCall(self, response):
        print "rejected, got %r"%(response,)
        d, self.d = self.d, None
        d.errback(response)

    def getVisibleAddress(self):
        return  ('127.0.0.1', 9876)


    def dropCall(self):
        print "drop"
        if hasattr(self,'cookie'):
            self.sip.app.endCall(self.cookie)
        else:
            print "'cancelling' non-started call"
        self.sip.callEndedRestartChecking()


    def terminateCall(self):
        print "remote end closed call"
        self.sip.app.endCall(self.cookie)
        self.sip.callEndedRestartChecking()


class TestSip:
    callFile = 'call.txt'

    "Just like shtoom.sip.SipProtocol, only not"
    def __init__(self, app):
        from twisted.internet import reactor
        self.app = app
        self.lastCall = time()
        reactor.callLater(5, self.checkForCallFile)

    def checkForCallFile(self):
        import os
        from twisted.internet import reactor
        reactor.callLater(5, self.checkForCallFile)
        if os.path.exists(self.callFile):
            s = os.stat(self.callFile)
            if s.st_mtime > self.lastCall:
                self.lastCall = time()
                if hasattr(self, 'c'):
                    print "'remote' end closing connection"
                    self.dropFakeInbound('foo')
                else:
                    print "new incoming call starting"
                    uri = open(self.callFile).readline().strip()
                    d = self.fakeInbound(uri)
                    d.addCallbacks(self._cb_fakeInbound,
                                   self._eb_fakeInbound).addErrback(log.err)

    def _cb_fakeInbound(self, response):
        print "fake inbound call setup OK,",response

    def _eb_fakeInbound(self, failure):
        print "fake inbound call setup failed,",failure
        self.callEndedRestartChecking()

    def callEndedRestartChecking(self):
        from twisted.internet import reactor
        print "restarting callfile checking"
        del self.c
        reactor.callLater(5, self.checkForCallFile)

    def placeCall(self, uri):
        self.c = TestCall(self)
        d = self.c.startCall()
        self.c.startFakeOutbound(uri)
        return d

    def dropCall(self, cookie):
        print "Sip.dropCall"
        self.c.dropCall()
        del self.c

    def register(self):
        pass

    def fakeInbound(self, uri):
        self.c = TestCall(self, uri)
        d = self.c.startCall()
        self.c.startFakeInbound()
        return d

    def dropFakeInbound(self, result):
        print "remote bye"
        self.c.terminateCall()


class EchoRTP:
    "A fake RTP layer that just repeats back any data sent to it"

    actions = []
    def __init__(self, app, cookie):
        self.cookie = cookie
        self.app = app
        self.go = False

    def createRTPSocket(self, ip, stun):
        self.actions.append('create')
        return defer.succeed(self.cookie)

    def start(self, remote):
        from twisted.internet.task import LoopingCall
        self.actions.append('start')
        self.go = True
        self.echo = ''
        self.LC = LoopingCall(self.mic_event)
        self.LC.start(0.020)

    def stopSendingAndReceiving(self):
        self.actions.append('stop')
        self.LC.stop()
        self.echo = ''

    def mic_event(self):
        from twisted.internet import reactor
        self.echo = self.app.giveSample(self.cookie)
        if self.echo is not None:
            packet = self.echo
            reactor.callLater(0, lambda : self.app.incomingRTP(self.cookie,
                                                              packet))

def main():
    from shtoom.app.phone import Phone
    import sys
    global app
    app = Phone()
    app._NATMapping = False
    app._rtpProtocolClass = EchoRTP
    app.boot(args=sys.argv[1:])
    app.sipListener.stopListening()
    del app.sip, app.sipListener
    app.sip = TestSip(app)
    app.start()
    sys.exit(0)

if __name__ == "__main__":
    from shtoom import i18n
    i18n.install()
    main()
