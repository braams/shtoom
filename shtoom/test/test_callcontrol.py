
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

class TestUI:

    def cb_callStarted(self, cookie):
        pass

    def cb_callFailed(self, cookie, message=None):
        pass

    def callConnected(self, cookie):
        pass

    def callDisconnected(self, cookie, reason):
        pass

    def incomingCall(self, description, cookie, defresp):
        pass

    def placeCall(self):
        pass

    def dropCall(self):
        pass

class TestCall:
    "A fake Call object"

class TestSIP
    "Just like shtoom.sip.Sip, only not"
    def placeCall(self, uri):
        pass
