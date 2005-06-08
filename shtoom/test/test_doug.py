# Copyright (C) 2004 Anthony Baxter
"""Tests for shtoom.doug

   These tests test doug DTMF send and receive
"""

from twisted.trial import unittest, util

from twisted.internet import defer, reactor

from shtoom.doug import VoiceApp
from shtoom.app.doug import DougApplication
from shtoom.doug.events import *
from shtoom.exceptions import CallRejected
from shtoom.i18n import install as i18n_install
i18n_install()

class TestDougApplication(DougApplication):
    _trial_def = None
    needLogging = False
    configFileName = None

    def ringBack(self):
        # ring ring
        pass

    def notifyEvent(self, event, arg):
        # Okay.
        pass

    def acceptErrors(self, cookie, error):
        #print "cookie %s got error %r"%(cookie, error)
        if self._trial_def is not None:
            d, self._trial_def = self._trial_def, None
            reactor.callLater(0, d.errback, error)

    def acceptResults(self, cookie, result):
        #print "cookie %s got result %r"%(cookie, result)
        if self._trial_def is not None:
            d, self._trial_def = self._trial_def, None
            reactor.callLater(0, d.callback, result)

class NullApp(VoiceApp):
    """ This application does nothing but return """

    def __start__(self):
        #print "started!"
        self.returnResult('hello world')

class NullListenApp(VoiceApp):
    """ This application does nothing but return """

    def __start__(self):
        #print "started!"
        return ( ( CallStartedEvent, self.started), )

    def started(self, event):
        event.leg.rejectCall(CallRejected('you suck'))
        self.returnResult('hello world')

class SimpleListenApp(VoiceApp):
    """ This application listens, connects a call, then either disconnects
        it, or waits for the other end to disconnect it
    """

    localDisconnect = True

    def __start__(self):
        return ( ( CallStartedEvent, self.started), )

    def started(self, evt):
        evt.leg.answerCall(self)
        return ( (CallAnsweredEvent, self.callAnswered),
                 (Event,            self.unknownEvent),
               )

    def callAnswered(self, evt):
        if self.localDisconnect:
            reactor.callLater(0, evt.leg.hangupCall)
        return ( (CallEndedEvent, self.done),
                 (Event,            self.unknownEvent),
               )

    def done(self, evt):
        self.returnResult('hello world')

    def unknownEvent(self, evt):
        self.returnResult(repr(evt))

class SimpleCallApp(VoiceApp):
    """ This application places a call, then then either disconnects
        it, or waits for the other end to disconnect it
    """
    _statemachine_debug = True
    callURL = None
    localDisconnect = False

    def __start__(self):
        return ( ( CallStartedEvent, self.started), )

    def started(self, evt):
        self.placeCall(self.callURL, 'sip:test@127.0.0.1')
        return ( (CallAnsweredEvent, self.callAnswered),
                 (CallRejectedEvent, self.callFailed),
                 (Event,             self.unknownEvent),
               )

    def callAnswered(self, evt):
        if self.localDisconnect:
            reactor.callLater(0, evt.leg.hangupCall)
        return ( (CallEndedEvent, self.done),
                 (Event,          self.unknownEvent),
               )

    def done(self, evt):
        self.returnResult('completed')

    def unknownEvent(self, evt):
        self.returnResult(repr(evt))

    def callFailed(self, evt):
        self.returnResult('failed')



class AudioSendingApp(VoiceApp):
    """ This test application simply connects to a remote address and sends
        an audio file
    """

class DTMFReceivingApp(VoiceApp):
    """ This test application listens for a connection, then accepts it
        and returns any DTMF that is sent
    """

def getDTMFAudioFile():
    from twisted.python.util import sibpath
    return sibpath(__file__, 'dtmftestfile.raw')

class Saver:
    val = None
    def save(self, v):
        self.val = v
        return v

class DougDTMFTest(unittest.TestCase):

    def setUp(self):
        import shtoom.nat
        shtoom.nat._forceMapper(shtoom.nat.NullMapper())
        shtoom.nat.clearCache()

    def tearDown(self):
        import shtoom.nat
        shtoom.nat._forceMapper(None)
        shtoom.nat.clearCache()

    def test_nullDougApp(self):
        app = TestDougApplication(NullApp)
        app.configFileName = None
        app.boot(args=['--listenport', '0'])
        app._voiceappArgs = {}
        d = app._trial_def = defer.Deferred()
        s = Saver()
        d.addCallback(s.save)
        # We explicitly start the voiceapp here
        reactor.callLater(0, app.startVoiceApp)
        util.wait(d)
        self.assertEquals(s.val, 'hello world')
        app.stopSIP()

    # This test is fundamentally broken.
    def not_test_callAndStartup(self):
        lapp = TestDougApplication(NullListenApp)
        lapp.boot(args=['--listenport', '0'])
        # Now get the port number we actually listened on
        port = lapp.sipListener.getHost().port
        lapp._voiceappArgs = {}
        d = lapp._trial_def = defer.Deferred()
        s = Saver()
        d.addCallback(s.save)
        capp = TestDougApplication(SimpleCallApp)
        capp.boot(args=['--listenport', '0'])
        capp._voiceappArgs = {'callURL': 'sip:foo@127.0.0.1:%d'%port }
        reactor.callLater(0, capp.startVoiceApp)
        util.wait(d)
        self.assertEquals(s.val, 'hello world')
        lapp.stopSIP()
        capp.stopSIP()

    def test_callStartupAndConnecting(self):
        lapp = TestDougApplication(SimpleListenApp)
        lapp.boot(args=['--listenport', '0'])
        # Now get the port number we actually listened on
        port = lapp.sipListener.getHost().port
        lapp._voiceappArgs = {}
        d1 = lapp._trial_def = defer.Deferred()
        s1 = Saver()
        d1.addCallback(s1.save)
        capp = TestDougApplication(SimpleCallApp)
        capp.boot(args=['--listenport', '0'])
        capp._voiceappArgs = {'callURL': 'sip:foo@127.0.0.1:%d'%port }
        d2 = capp._trial_def = defer.Deferred()
        s2 = Saver()
        d2.addCallback(s2.save)
        reactor.callLater(0, capp.startVoiceApp)
        util.wait(d1)
        util.wait(d2)
        self.assertEquals(s1.val, 'hello world')
        self.assertEquals(s2.val, 'completed')
        lapp.stopSIP()
        capp.stopSIP()
