# Copyright (C) 2004 Anthony Baxter
"""Tests for SDP.

You can run this with command-line:

  $ trial shtoom.test.test_sdp
"""

from twisted.trial import unittest
from twisted.internet import reactor, defer

from shtoom.doug.events import Event, CallStartedEvent
from shtoom.doug.voiceapp import VoiceApp

class DummyEvent1(Event): pass
class DummyEvent2(Event): pass
class DummyEvent2_1(DummyEvent2): pass
class DummyEvent2_2(DummyEvent2): pass

class UnknownEventError(Exception): pass


class TestStateMachine(VoiceApp):
    def __init__(self, defer, **kwargs):
        self._out = []
        super(TestStateMachine, self).__init__(defer, **kwargs)

    def __start__(self):
        print "starting"
        return ( (CallStartedEvent, self.begin),
                 (Event, self.unknown),
               )

    def unknown(self, evt):
        raise ValueError, "got unknown event %s"%(evt.getEventName())

    def begin(self, evt):
        self._out.append(0)
        self.raiseEvent(DummyEvent1())
        return ( (DummyEvent1, self.first),
                 (Event, self.unknown),
               )

    def first(self, evt):
        self._out.append(1)
        self.raiseEvent(DummyEvent2_1())
        return ( (DummyEvent2, self.second),
                 (Event, self.unknown),
               )

    def second(self, evt):
        self._out.append(2)
        self.raiseEvent(DummyEvent2_2())
        return ( (DummyEvent2_1, self.thirdish),
                 (Event, self.third),
               )

    def thirdish(self, evt):
        raise ValueError, "wrong event hit"

    def third(self, evt):
        self._out.append(3)
        self.returnResult(self._out)


class StateMachineTest(unittest.TestCase):
    def testStateMachine(self):
        d = defer.Deferred()
        A = TestStateMachine(d)
        reactor.callLater(0, A._start)
        self.assertEquals(unittest.deferredResult(d), [0,1,2,3])

