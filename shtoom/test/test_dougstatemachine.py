# Copyright (C) 2004 Anthony Baxter
"""Tests for SDP.

You can run this with command-line:

  $ trial shtoom.test.test_sdp
"""

from twisted.trial import unittest, util
from twisted.internet import reactor, defer
from twisted.python.failure import Failure

from shtoom.doug.events import Event, CallStartedEvent
from shtoom.doug.statemachine import StateMachine
from shtoom.doug.exceptions import *

class DummyEvent1(Event): pass
class DummyEvent2(Event): pass
class DummyEvent2_1(DummyEvent2): pass
class DummyEvent2_2(DummyEvent2): pass

class StateMachineOne(StateMachine):
    def __init__(self, defer, **kwargs):
        self._out = []
        super(StateMachineOne, self).__init__(defer, **kwargs)

    def __start__(self):
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

class StateMachineTwo(StateMachineOne):
    def second(self, evt):
        self.raiseEvent(DummyEvent2_2())
        return ()

class StateMachineThree(StateMachineTwo):
    def second(self, evt):
        from twisted.internet import reactor, defer
        self._out.append(2)
        d = defer.Deferred()
        reactor.callLater(0.1, self._triggerEvent, DummyEvent2_2())
        reactor.callLater(0.2, d.callback,
                                 ((DummyEvent2_1, self.thirdish),
                                  (Event, self.third),)
                         )
        return d

class Saver:
    res = None
    err = None
    def save(self, res):
        self.res = res
    def error(self, err):
        self.err = err

class StateMachineTest(unittest.TestCase):
    def testStateMachine(self):
        d = defer.Deferred()
        A = StateMachineOne(d)
        reactor.callLater(0, A._start)
        s = Saver()
        d.addCallback(s.save)
        util.wait(d)
        self.assertEquals(s.res, [0,1,2,3])

    def testStateMachineWithDeferreds(self):
        d = defer.Deferred()
        A = StateMachineThree(d)
        reactor.callLater(0, A._start)
        class Saver:
            res = None
            def save(self, res):
                self.res = res
        s = Saver()
        d.addCallback(s.save)
        util.wait(d)
        self.assertEquals(s.res, [0,1,2,3])


    def testBrokenStateMachine(self):
        d = defer.Deferred()
        A = StateMachineTwo(d)
        reactor.callLater(0, A._start)
        s = Saver()
        d.addCallback(s.save)
        d.addErrback(s.error)
        util.wait(d)
        self.assertEquals(s.res, None)
        self.assert_(isinstance(s.err.value, EventNotSpecifiedError))
