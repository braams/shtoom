
from twisted.python import log
from shtoom.ui.base import ShtoomBaseUI
from twisted.internet import stdio
from twisted.protocols import basic

class ShtoomMain(basic.LineReceiver, ShtoomBaseUI):
    _connected = None
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
        log.msg("error %s"%(message))

    def shutdown(self):
        # XXX Hang up any calls
        from twisted.internet import reactor
        reactor.stop()

    def incomingCall(self, description, call, defresp, defsetup):
        self._pending = ( call, defresp, defsetup )
        self.transport.write("INCOMING CALL: %s\n"%description)
        self.transport.write("Type 'accept' to accept, 'reject' to reject\n")

    def connectionMade(self):
        self.transport.write("Welcome to shtoom\n>> ")

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
        if self._connected is not None:
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
        self._connected, deferred = self.sip.placeCall(self.sipURL)
        deferred.addCallbacks(self.callConnected, self.callDisconnected)

    def callConnected(self, call):
        log.msg("Call to %s CONNECTED"%(self.sipURL))

    def callDisconnected(self, call):
        log.msg("Call to %s DISCONNECTED"%(self.sipURL))

    def cmd_hangup(self, line):
        if self._connected is not None:
            self.sip.dropCall(self._connected)
            self._connected = None
        else:
            self.transport.write("error: no active call\n")

    def cmd_quit(self, line):
        self.shutdown()

    def cmd_accept(self, line):
        if not self._pending:
            self.transport.write("no pending calls")
            return
        self._connected, resp, setup = self._pending
        self._pending = None
        setup.addCallbacks(self.callConnected, self.callDisconnected)
        resp.callback('yes')

    def cmd_reject(self, line):
        if not self._pending:
            self.transport.write("no pending calls")
            return
        self._connected, resp, setup = self._pending
        self._pending = None
        resp.errback('no')
