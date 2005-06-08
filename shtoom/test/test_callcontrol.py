from twisted.internet import reactor, defer
from twisted.python import log
import twisted.trial.util
from shtoom.i18n import install as i18n_install
i18n_install()

#TDEBUG=True
TDEBUG=False

callFlowOutboundHorror = """
For an outbound call:
  UI calls app.placeCall(), which calls sip.SIP.placeCall(), which
  returns a deferred (compDef). The UI attaches cb_callStarted and
  cb_callFailed to this.
  compDef is passed off to the newly created sip.Call() object.
  The new Call object calls app.acceptCall() with a calltype of
  'outbound'. This returns a deferred (generally, triggered
  immediately) with the new 'cookie' for the call. This deferred
  triggers Call.sendInvite().
  Call.sendInvite() calls app.getSDP(cookie) to get the SDP of the call.
  If the call fails or is rejected, the compDef.errback() is called.
  No method of the app gets notified of this. Oops.
  If the call succeeds, app.startCall() is called, and passed the
  callcookie, the remote end's RTP (host,port), and compDef.callback
  This then starts RTP and triggers the compDef callback with the
  cookie.

  To Do:
  app.startCall() should be attached to the deferred returned by
  SIP.placeCall(). This should be passed the Call object on success,
  startCall should then return defer.succeed(callcookie) which will
  be passed on to the UI.
"""

callFlowInboundHorror = """
  An invite message is received by sip.SIP(). This creates a new
  deferred (compDef) and creates a sip.Call() object, passing in
  compDef. It then calls Call.startInboundCall(), and here is where
  the horror begins.

  Call.setupLocalSIP() returns a deferred. We chain some callbacks on to
  this:
     Call.recvInvite()
     app.acceptCall(), which itself returns a deferred
     (Call.acceptedCall(), Call.rejectedCall())
"""

class TestAudio:
    def __init__(self):
        self.actions = []

    def selectDefaultFormat(self, fmt):
        self.actions.append('select')
        if TDEBUG: print "selecting fake audio format"

    def listFormat(self):
        self.actions.append('list')
        return []

    def reopen(self, mediahandler):
        self.actions.append('reopen')
        if TDEBUG: print "reopening fake audio"

    def close(self):
        self.actions.append('close')
        if TDEBUG: print "closing fake audio"

    def read(self):
        self.actions.append('read')
        return ''

    def write(self, bytes):
        self.actions.append('write')
        pass

    def playWaveFile(self, file):
        self.actions.append('wave')
        pass

class TestUI:
    threadedUI = False
    cookie = None

    def __init__(self, stopOnDisconnect=True):
        self.stopOnDisconnect = stopOnDisconnect
        self.actions = []

    def statusMessage(self, *args):
        pass

    def connectApplication(self, app):
        self.app = app

    def statusMessage(self, mess):
        # mess
        pass

    def callStarted(self, cookie):
        self.actions.append(('start',cookie))
        self.cookie = cookie
        if TDEBUG: print "callStarted", self.cookie

    def cb_callFailed(self, cookie, message=None):
        self.actions.append(('failed',cookie))
        if TDEBUG: print "callFailed", cookie

    def cb_callConnected(self, cookie):
        if TDEBUG: print "callConnected", self.cookie
        self.actions.append(('connected',cookie))

    def callDisconnected(self, cookie, reason):
        self.actions.append(('disconnected',cookie))
        if TDEBUG: print "callDisconnected", self.cookie
        if self.stopOnDisconnect:
            self.compdef.callback(None)

    def incomingCall(self, description, cookie):
        if TDEBUG: print "incoming"
        self.actions.append(('incoming',cookie))
        self.cb_callConnected(cookie)
        d = defer.succeed(cookie)
        return d

    def fakeCall(self):
        if TDEBUG: print "placing a call"
        d = self.app.placeCall('sip:foo@bar')
        d.addCallbacks(self.cb_callConnected,
                       self.cb_callFailed).addErrback(log.err)

    def dropCall(self):
        self.actions.append(('drop',self.cookie))
        self.app.dropCall(self.cookie)


class TestCall:
    "A fake Call object"
    def __init__(self, d, sip):
        self.d = d
        self.sip = sip

    def getLocalSIPAddress(self):
        return ( '127.0.0.1', 5060)

    def getSTUNState(self):
        return False

    def startFakeInbound(self):
        from shtoom.sip import Dialog
        self.dialog = Dialog()
        self.dialog.setDirection(inbound=True)
        d = self.sip.app.acceptCall(call=self)
        d.addCallbacks(self.acceptedFakeCall,
                       self.rejectedFakeCall).addErrback(log.err)

    def startFakeOutbound(self, uri):
        from shtoom.sip import Dialog
        self.dialog = Dialog()
        self.dialog.setDirection(outbound=True)
        d = self.sip.app.acceptCall(call=self)
        d.addCallbacks(self.acceptedFakeCall,
                       self.rejectedFakeCall).addErrback(log.err)

    def acceptedFakeCall(self, cookie):
        from shtoom.sdp import SDP, MediaDescription
        s = SDP()
        s.setServerIP('127.0.0.1')
        md = MediaDescription()
        s.addMediaDescription(md)
        md.setLocalPort(9876)
        if TDEBUG: print "accepted, got %r"%(cookie,)
        self.cookie = cookie
        d, self.d = self.d, None
        self.sip.app.startCall(self.cookie, s, d.callback)

    def rejectedFakeCall(self, e):
        if TDEBUG: print "rejected, got %r"%(e,)
        d, self.d = self.d, None
        d.errback(e)

    def dropCall(self):
        if TDEBUG: print "drop"
        self.sip.app.endCall(self.cookie)

    def terminateCall(self):
        if TDEBUG: print "remote end closed call"
        self.sip.app.endCall(self.cookie)


class TestSip:
    "Just like shtoom.sip.SipProtocol, only not"
    def __init__(self, app):
        self.app = app

    def placeCall(self, uri):
        d = defer.Deferred()
        self.c = TestCall(d, self)
        self.c.startFakeOutbound(uri)
        return d

    def register(self):
        pass

    def fakeInbound(self):
        d = defer.Deferred()
        self.c = TestCall(d, self)
        self.c.startFakeInbound()
        return d

    def dropFakeInbound(self, result):
        if TDEBUG: print "remote bye"
        self.c.terminateCall()

    def dropCall(self, cookie):
        if TDEBUG: print "dropCall"
        self.c.dropCall()

class TestRTP:
    actions = []
    def __init__(self, app, cookie):
        self.cookie = cookie
        self.app = app

    def createRTPSocket(self, ip, stun):
        self.actions.append('create')
        return defer.succeed(self.cookie)

    def start(self, remote):
        self.actions.append('start')
        pass

    def stopSendingAndReceiving(self):
        self.actions.append('stop')
        pass

from twisted.trial import unittest

class TestCallControl(unittest.TestCase):

    def testOutboundLocalBye(self, loopcount=4):
        from shtoom.app.phone import Phone
        ui = TestUI()
        au = TestAudio()
        p = Phone(ui=ui, audio=au)
        p._rtpProtocolClass = TestRTP
        ui.connectApplication(p)
        p.connectSIP = lambda x=None: None
        p._startReactor = False
        p.boot(args=[])
        p.sip = TestSip(p)
        for l in range(loopcount):
            testdef = ui.compdef = defer.Deferred()
            TestRTP.actions = []
            reactor.callLater(0, ui.fakeCall)
            reactor.callLater(0, ui.dropCall)
            p.start()
            twisted.trial.util.wait(testdef)
            self.assertEquals(au.actions, ['close', 'select', 'reopen', 'close'])
            self.assertEquals(TestRTP.actions, ['create', 'start', 'stop'])
            actions = ui.actions
            if TDEBUG: print actions
            cookie = actions[0][1]
            for a,c in actions[1:]:
                self.assertEquals(cookie,c)
            actions = [x[0] for x in actions]
            self.assertEquals(actions, ['start', 'connected', 'drop', 'disconnected'])
            ui.actions = []
            au.actions = []

    def testOutboundRemoteBye(self):
        from shtoom.app.phone import Phone
        ui = TestUI()
        au = TestAudio()
        p = Phone(ui=ui, audio=au)
        p._startReactor = False
        TestRTP.actions = []
        p._rtpProtocolClass = TestRTP
        ui.connectApplication(p)
        testdef = ui.compdef = defer.Deferred()
        reactor.callLater(0, ui.fakeCall)
        p.connectSIP = lambda x=None: None
        p.boot(args=[])
        p.sip = TestSip(p)
        reactor.callLater(0.3, lambda : p.sip.dropCall(ui.cookie))
        p.start()
        twisted.trial.util.wait(testdef)
        self.assertEquals(au.actions, ['close', 'select', 'reopen', 'close'])
        self.assertEquals(TestRTP.actions, ['create', 'start', 'stop'])
        actions = ui.actions
        cookie = actions[0][1]
        for a,c in actions[1:]:
            self.assertEquals(cookie,c)
        actions = [x[0] for x in actions]
        self.assertEquals(actions, ['start', 'connected', 'disconnected'])
        if TDEBUG: print actions

    def testInboundRemoteBye(self):
        from shtoom.app.phone import Phone
        ui = TestUI()
        au = TestAudio()
        p = Phone(ui=ui, audio=au)
        p._startReactor = False
        TestRTP.actions = []
        p._rtpProtocolClass = TestRTP
        ui.connectApplication(p)
        testdef = ui.compdef = defer.Deferred()
        p.connectSIP = lambda x=None: None
        p.boot(args=[])
        p.sip = TestSip(p)
        d =  p.sip.fakeInbound()
        d.addCallback(p.sip.dropFakeInbound)
        p.start()
        twisted.trial.util.wait(testdef)
        self.assertEquals(au.actions, ['wave', 'close', 'select', 'reopen', 'close'])
        self.assertEquals(TestRTP.actions, ['create', 'start', 'stop'])
        actions = ui.actions
        cookie = actions[0][1]
        if TDEBUG: print actions
        for a,c in actions[1:]:
            self.assertEquals(cookie,c)
        actions = [x[0] for x in actions]
        # XXX no connected??
        self.assertEquals(actions, ['incoming', 'connected', 'start', 'disconnected'])
