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
    def selectFormat(self, fmt): 
        print "selecting fake audio format"

    def listFormat(self):
        return []

    def reopen(self):
        print "reopening fake audio"

    def close(self):
        print "closing fake audio"

    def read(self):
        return ''

    def write(self, bytes):
        pass

class TestUI:

    def connectApplication(self, app):
        self.app = app

    def callStarted(self, cookie):
        self.cookie = cookie
        print "callStarted", self.cookie

    def cb_callFailed(self, cookie, message=None):
        print "callFailed", self.cookie

    def cb_callConnected(self, cookie):
        print "callConnected", self.cookie
        reactor.callLater(0, self.dropCall)

    def callDisconnected(self, cookie, reason):
        print "callDisconnected", self.cookie
        reactor.stop()

    def incomingCall(self, description, cookie):
        print "incoming"
        return defer.succeed('PretendCookie #1')

    def fakeCall(self):
        print "placing a call"
        d = self.app.placeCall('sip:foo@bar')
        d.addCallbacks(self.cb_callConnected, 
                       self.cb_callFailed).addErrback(log.err)

    def dropCall(self):
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
        self.sip.app.endCall(self.cookie)


class TestSip:
    "Just like shtoom.sip.SipPhone, only not"
    def __init__(self, app):
        self.app = app

    def placeCall(self, uri):
        d = defer.Deferred()
        c = TestCall(d, self)
        c.startFakeOutbound(uri)
        return d

    def register(self):
        pass

class TestRTP:
    def __init__(self, app, cookie):
        self.cookie = cookie
        self.app = app

    def createRTPSocket(self, ip, stun):
        return defer.succeed('ok')

    def startSendingAndReceiving(self, remote):
        pass

    def stopSendingAndReceiving(self):
        pass

from twisted.trial import unittest

class TestCallControl(unittest.TestCase):
    def testOutbound(self):
        from shtoom.app.phone import Phone
        ui = TestUI()
        p = Phone(ui=ui, audio=TestAudio())
        p._rtpProtocolClass = TestRTP
        ui.connectApplication(p)
        reactor.callLater(0, ui.fakeCall)
        p.boot()
        p.sip = TestSip(p)
        p.start()

