
from twisted.python import log
from shtoom.ui.base import ShtoomBaseUI
from twisted.internet import stdio, defer
from twisted.protocols import basic

class ShtoomMain(basic.LineReceiver, ShtoomBaseUI):
    _cookie = None
    _pending = None
    _debug = True
    from os import linesep as delimiter

    def debugMessage(self, msg):
        if self._debug:
            print msg

    def statusMessage(self, msg):
        if self._debug:
            print "status", msg

    def errorMessage(self, message, exc=None):
        log.msg("error %s"%(message), system='ui')

    def shutdown(self):
        # XXX Hang up any calls
        if self._cookie:
            self.app.dropCall(self._cookie)
        from twisted.internet import reactor
        reactor.stop()

    def incomingCall(self, description, cookie, defsetup):
        defresp = defer.Deferred()
        self._pending = ( cookie, defresp )
        self.transport.write("INCOMING CALL: %s\n"%description)
        self.transport.write("Type 'accept' to accept, 'reject' to reject\n")
        defsetup.addCallback(lambda x: defresp)

    def connectionMade(self):
        self.transport.write("Welcome to shtoom\n>> \n")

    def lineReceived(self, line):
        args = line.strip().split()
        if args:
            cmd = args[0].lower()
            if hasattr(self, "cmd_%s"%cmd):
                getattr(self, "cmd_%s"%(cmd))(line)
            elif cmd == "?":
                self.cmd_help(line)
            else:
                self.transport.write("Unknown command '%s'\n"%(cmd))
        self.transport.write(">> ")

    def cmd_help(self, line):
        methods = [ x[4:] for x in dir(self) if x[:4] == "cmd_" ]
        self.transport.write("Commands: %s\n"%(' '.join(methods)))

    def cmd_call(self, line):
        if self._cookie is not None:
            self.transport.write("error: only one call at a time for now\n")
            return
        args = line.split()
        if len(args) != 2:
            self.transport.write("error: call <sipurl>\n")
            return
        if not args[1].startswith('sip:'):
            self.transport.write("error: call <sipurl>\n")
            return
        self.sipURL = args[1]
        deferred = self.app.placeCall(self.sipURL)
        deferred.addCallbacks(self.callConnected, self.callFailed).addErrback(log.err)

    def callStarted(self, cookie):
        self._cookie = cookie
        log.msg("Call to %s STARTED"%(self.sipURL), system='ui')

    def callConnected(self, cookie):
        log.msg("Call to %s CONNECTED"%(self.sipURL), system='ui')

    def callFailed(self, e, message=None):
        log.msg("Call to %s FAILED: %r"%(self.sipURL, e), system='ui')

    def callDisconnected(self, cookie, message):
        log.msg("Call to %s DISCONNECTED"%(self.sipURL), system='ui')
        self._cookie = None

    def cmd_hangup(self, line):
        if self._cookie is not None:
            self.app.dropCall(self._cookie)
            self._cookie = None
        else:
            self.transport.write("error: no active call\n")

    def cmd_quit(self, line):
        self.shutdown()

    def cmd_accept(self, line):
        if not self._pending:
            self.transport.write("no pending calls")
            return
        self._cookie, resp, setup = self._pending
        self._pending = None
        setup.addCallbacks(self.callConnected, self.callFailed).addErrback(log.err)
        resp.callback(self._cookie)

    def cmd_reject(self, line):
        if not self._pending:
            self.transport.write("no pending calls")
            return
        self._cookie, resp, setup = self._pending
        self._pending = None
        resp.errback('no')
