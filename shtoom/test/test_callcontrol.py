from twisted.internet import reactor, defer
from twisted.python import log
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
    def selectFormat(self, fmt): 
        self.actions.append('select')
        print "selecting fake audio format"

    def listFormat(self):
        self.actions.append('list')
        return []

    def reopen(self):
        self.actions.append('reopen')
        print "reopening fake audio"

    def close(self):
        self.actions.append('close')
        print "closing fake audio"

    def read(self):
        self.actions.append('read')
        return ''

    def write(self, bytes):
        self.actions.append('write')
        pass

class TestUI:
    threadedUI = False

    def __init__(self):
        self.actions = []

    def connectApplication(self, app):
        self.app = app

    def callStarted(self, cookie):
        self.actions.append(('start',cookie))
        self.cookie = cookie
        print "callStarted", self.cookie

    def cb_callFailed(self, cookie, message=None):
        self.actions.append(('failed',cookie))
        print "callFailed", self.cookie

    def cb_callConnected(self, cookie):
        print "callConnected", self.cookie
        self.actions.append(('connected',cookie))
        reactor.callLater(0, self.dropCall)

    def callDisconnected(self, cookie, reason):
        self.actions.append(('disconnected',cookie))
        print "callDisconnected", self.cookie
        reactor.stop()

    def incomingCall(self, description, cookie):
        print "incoming"
        self.actions.append(('incoming',cookie))
        return defer.succeed(cookie)

    def fakeCall(self):
        print "placing a call"
        d = self.app.placeCall('sip:foo@bar')
        d.addCallbacks(self.cb_callConnected, 
                       self.cb_callFailed).addErrback(log.err)

    def dropCall(self):
        print "dropping connected call"
        self.actions.append(('drop',self.cookie))
        self.app.dropCall(self.cookie)
        print "dropped"

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
        print "accepted, got %r"%(cookie,)
        self.cookie = cookie
        d, self.d = self.d, None
        self.sip.app.startCall(self.cookie, ('127.0.0.1', 9876), d.callback)

    def rejectedFakeCall(self, e):
        print "rejected, got %r"%(e,)
        d, self.d = self.d, None
        d.errback(e)

    def dropCall(self):
        print "drop"
        self.sip.app.endCall(self.cookie)


class TestSip:
    "Just like shtoom.sip.SipPhone, only not"
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
        self.c.dropCall()

    def dropCall(self, cookie):
        print "dropCall"
        self.c.dropCall()

class TestRTP:
    actions = []
    def __init__(self, app, cookie):
        self.cookie = cookie
        self.app = app

    def createRTPSocket(self, ip, stun):
        self.actions.append('create')
        return defer.succeed('ok')

    def startSendingAndReceiving(self, remote):
        self.actions.append('start')
        pass

    def stopSendingAndReceiving(self):
        self.actions.append('stop')
        pass

from twisted.trial import unittest

class TestCallControl(unittest.TestCase):
    def testOutbound(self):
        from shtoom.app.phone import Phone
        ui = TestUI()
        au = TestAudio()
        p = Phone(ui=ui, audio=au)
        TestRTP.actions = []
        p._rtpProtocolClass = TestRTP
        ui.connectApplication(p)
        reactor.callLater(0, ui.fakeCall)
        p.connectSIP = lambda x=None: None 
        p.boot()
        p.sip = TestSip(p)
        p.start()
        self.assertEquals(au.actions, ['reopen', 'close'])
        self.assertEquals(TestRTP.actions, ['create', 'start', 'stop'])
        actions = ui.actions
        cookie = actions[0][1]
        for a,c in actions[1:]:
            self.assertEquals(cookie,c)
        actions = [x[0] for x in actions]
        self.assertEquals(actions, ['start', 'connected', 'drop', 'disconnected'])
        print actions

    def testInbound(self):
        from shtoom.app.phone import Phone
        ui = TestUI()
        au = TestAudio()
        p = Phone(ui=ui, audio=au)
        TestRTP.actions = []
        p._rtpProtocolClass = TestRTP
        ui.connectApplication(p)
        p.connectSIP = lambda x=None: None 
        p.boot()
        p.sip = TestSip(p)
        d =  p.sip.fakeInbound()
        d.addCallback(p.sip.dropFakeInbound)
        p.start()
        self.assertEquals(au.actions, ['reopen', 'close'])
        self.assertEquals(TestRTP.actions, ['create', 'start', 'stop'])
        actions = ui.actions
        cookie = actions[0][1]
        for a,c in actions[1:]:
            self.assertEquals(cookie,c)
        actions = [x[0] for x in actions]
        # XXX no connected??
        self.assertEquals(actions, ['start', 'incoming', 'connected', 'disconnected'])
        
