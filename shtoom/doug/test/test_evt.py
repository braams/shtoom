# Copyright (C) 2004 Anthony Baxter
"""Tests for SDP.

You can run this with command-line:

  $ trial shtoom.test.test_sdp
"""

#from twisted.trial import unittest
from twisted.internet import reactor, defer

from shtoom.doug.events import Event, CallStartedEvent
from shtoom.doug.voiceapp import VoiceApp

class DummyEvent1(Event): pass
class DummyEvent2(Event): pass
class DummyEvent2_1(DummyEvent2): pass
class DummyEvent2_2(DummyEvent2): pass


class EventLoop(VoiceApp):
    def __start__(self):
        print "starting"
        return ( (CallStartedEvent, self.begin),
                 (Event, self.unknown),
               )

    def unknown(self, evt):
        print "got unknown event %s"%(evt.getEventName())
        reactor.stop()
        return ()

    def begin(self, evt):
        print "beginning", evt
        self.raiseEvent(DummyEvent1())
        return ( (DummyEvent1, self.first),
                 (Event, self.unknown),
               )

    def first(self, evt):
        print "stage the first", evt
        self.raiseEvent(DummyEvent2_1())
        return ( (DummyEvent2, self.second),
                 (Event, self.unknown),
               )

    def second(self, evt):
        print "stage the second", evt
        self.raiseEvent(DummyEvent2_2())
        return ( (DummyEvent2_1, self.third),
                 (Event, self.unknown),
               )

    def third(self, evt):
        print "third (should not be hit)", evt
        return ()

def test():
    d = defer.Deferred()
    A = EventLoop(d)
    reactor.callLater(0, A._start)
    reactor.run()

if __name__ == "__main__":
    test()
