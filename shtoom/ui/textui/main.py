
from twisted.python import log
from shtoom.ui.base import ShtoomBaseUI
from twisted.internet import stdio, defer
from twisted.protocols import basic
from shtoom.exceptions import CallRejected, CallNotAnswered

from gettext import gettext as _

class ShtoomMain(basic.LineReceiver, ShtoomBaseUI):
    _cookie = None
    _pending = None
    _debug = True
    _incoming_timeout = None
    from os import linesep as delimiter
    sipURL = None

    def debugMessage(self, msg):
        if self._debug:
            print msg

    def statusMessage(self, msg):
        if self._debug:
            print "status", msg

    def errorMessage(self, message, exc=None):
        log.msg("error %s"%(message), system='ui')

    def shutdown(self):
        from twisted.internet import reactor
        # XXX Hang up any calls
        if self._cookie:
            self.app.dropCall(self._cookie)
        reactor.stop()

    def incomingCall(self, description, cookie):
        from twisted.internet import reactor
        if self._pending is not None:
            return defer.fail(UserBusy())
        defresp = defer.Deferred()
        self._pending = ( cookie, defresp )
        self._incoming_timeout = reactor.callLater(20,
                        lambda :self._timeout_incoming(self._pending))
        self.transport.write("INCOMING CALL: %s\n"%description)
        self.transport.write("Type 'accept' to accept, 'reject' to reject\n")
        return defresp

    def connectionMade(self):
        self.transport.write("Welcome to shtoom, debug rev. %s\n>> \n" %
                                                    self.app._develrevision)

    def lineReceived(self, line):
        args = line.strip().split()
        if args:
            cmd = args[0].lower()
            if hasattr(self, "cmd_%s"%cmd):
                getattr(self, "cmd_%s"%(cmd))(line)
            elif cmd == "?":
                self.cmd_help(line)
            elif cmd.startswith('sip:'):
                self.cmd_call('call %s'%(cmd))
            else:
                self.transport.write("Unknown command '%s'\n"%(cmd))
        self.transport.write(">> ")

    def cmd_help(self, line):
        "help -- show help"
        methods = [ x for x in dir(self) if x[:4] == "cmd_" ]
        self.transport.write("Commands:\n")
        for m in methods:
            self.transport.write("%s\n"%(getattr(self, m).__doc__))

    def cmd_call(self, line):
        "call sip:whatever -- place a new outbound call"
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
        log.msg("Call %s STARTED"%(self._cookie), system='ui')

    def callConnected(self, cookie):
        log.msg("Call to %s CONNECTED"%(self.sipURL), system='ui')

    def callFailed(self, e, message=None):
        log.msg("Call to %s FAILED: %r"%(self.sipURL, e), system='ui')

    def callDisconnected(self, cookie, message):
        log.msg("Call to %s DISCONNECTED"%(self.sipURL), system='ui')
        self._cookie = None

    def cmd_hangup(self, line):
        "hangup -- hangs up current call"
        if self._cookie is not None:
            self.app.dropCall(self._cookie)
            self._cookie = None
        else:
            self.transport.write("error: no active call\n")

    def cmd_quit(self, line):
        "quit -- exit the program"
        self.shutdown()

    def cmd_accept(self, line):
        "accept -- accept an incoming call"
        if not self._pending:
            self.transport.write("no pending calls")
            return
        self._incoming_timeout.cancel()
        self._incoming_timeout = None
        self._cookie, resp = self._pending
        self._pending = None
        resp.callback(self._cookie)

    def cmd_reject(self, line):
        "reject -- reject an incoming call"
        self._incoming_timeout.cancel()
        self._incoming_timeout = None
        if not self._pending:
            self.transport.write("no pending calls")
            return
        cookie, resp = self._pending
        self._pending = None
        resp.callback(CallRejected('no thanks', cookie))

    def cmd_auth(self, line):
        "auth realm user password -- add a user/password"
        toks = line.split(' ')
        if len(toks) != 4:
            self.transport.write("usage: auth realm user password")
            return
        cmd, realm, user, password = toks
        self.app.creds.addCred(realm, user, password, save=True)

    def cmd_dtmf(self, line, duration=0.1, delay=0.1):
        "dtmf <digits> -- send dtmf key presses to the other end"
        from twisted.internet import reactor
        initial = 0.2
        toks = line.split(' ',1)
        for n, key in enumerate(toks[1]):
            if key not in '01234567890#*, ':
                self.transport.write('ignoring unknown key %r\n'%(key))
                continue
            if key in ' ,':
                # pause
                continue
            n = float(n)
            reactor.callLater(initial+n*(duration+delay),
                lambda k=key: self.app.startDTMF(self._cookie, k))
            reactor.callLater(initial+n*(duration+delay)+duration,
                lambda k=key: self.app.stopDTMF(self._cookie, k))

    def _timeout_incoming(self, which):
        # Not using 'which' for now
        self.transport.write("CALL NOT ANSWERED\n")
        self._incoming_timeout = None
        cookie, resp = self._pending
        self._pending = None
        resp.callback(CallNotAnswered('not answering', cookie))

    def ipcCommand(self, command, args):
        if command == 'call':
            if self._cookie is None:
                self.sipURL = args
                deferred = self.app.placeCall(self.sipURL)
                deferred.addCallbacks(self.callConnected,
                                      self.callFailed).addErrback(log.err)
                return _('Calling')
            else:
                return _('Already on a call')
        elif command == 'hangup':
            if self._cookie is not None:
                self.app.dropCall(self._cookie)
                self._cookie = None
            else:
                return _('No active call')
        elif command == 'accept':
            return _('Not implemented')
        elif command == 'reject':
            return _('Not implemented')
        elif command == 'quit':
            self.shutdown()
        else:
            log.msg('IPC got unknown message %s (args %r)'%(command, args))
