#!/usr/bin/env python
# Copyright (C) 2004 Anthony Baxter
"""Tests for shtoom.audio.playout
Hello I am not a unit test.  Run me explicitly from the cmdline.  Thank you.
"""

# from shtoom
import shtoom.audio.playout
# shtoom.audio.playout.DEBUG = True
from shtoom.audio.playout import Playout
from shtoom.audio.converters import MediaSample

# from the Twisted library
from twisted.internet import reactor, defer
from twisted.python import log

# from the Python Standard Library
import sys
log.startLogging(sys.stdout)


EPSILON=0.0001

SAMPLEHZ = 8000
SAMPLESIZE = 2
BPS = SAMPLEHZ * SAMPLESIZE

PACKETLEN=0.020

PACKETSIZE=int(PACKETLEN * BPS)

# We must give enough test packets to satisfy the playout object's desire to store up media in order to compensate for jitter.
TESTPACKETS=int(shtoom.audio.playout.JITTER_BUFFER_SECONDS * BPS / PACKETSIZE)

import datetime, time
def timestamp():
    return datetime.datetime.fromtimestamp(time.time()).isoformat(' ')

class DummyWriter:
    def __init__(self):
        self.b = []
        self.ts = []
    def write(self, data):
        self.b.append(data)
        self.ts.append(time.time())

class DummyMediaLayer:
    def __init__(self):
        self._d = DummyWriter()

class Tester:
    def __init__(self):
        self.dml = DummyMediaLayer()
        self.p = Playout(self.dml, )
        self.inb = []
        for i in range(TESTPACKETS):
            self.inb.append(str(i) + ('\x00' * (PACKETSIZE - len(str(i)))))
        self.i = 0
        log.msg("%s starting test: %s" % (timestamp(), self.__class__.__name__,))
        self.d = defer.Deferred()
        reactor.callLater(0, self.feed_next_packet)


def repr_buf_for_log(buf):
    return map(lambda x: x[:3], buf)

class EvenFlowTester(Tester):
    """
    If a steady flow of TESTPACKETS packets arrives, followed by a long silence, then the playout ought to play all TESTPACKETS of the packets.
    """
    def check_test(self):
        self.d.callback(None)
        assert self.dml._d.b == self.inb, "%s %s, %s" % (timestamp(), repr_buf_for_log(self.dml._d.b), repr_buf_for_log(self.inb),)
        log.msg("%s %s success" % (timestamp(), self,))

    def feed_next_packet(self):
        # log.msg("%s %s about to write %s, %s" % (timestamp(), self.__class__.__name__, `self.inb[self.i]`, self.i,))
        data = self.inb[self.i]
        self.p.write(data, self.i)
        self.i += 1
        if self.i < TESTPACKETS:
            reactor.callLater(max(0, (len(data) / float(BPS)) - EPSILON), self.feed_next_packet)
        else:
            reactor.callLater(max(0, ((len(data) * len(self.inb)) / float(BPS)) - EPSILON), self.check_test)


class OutOfOrderArrivalTester(Tester):
    """
    If a steady flow of TESTPACKETS packets arrives, but with each pair swapped, followed by a long silence, then the playout ought to play all TESTPACKETS of the packets (in the right order).
    """
    def check_test(self):
        self.d.callback(None)
        assert self.dml._d.b == self.inb, "%s, %s" % (self.dml._d.b, self.inb,)
        log.msg("%s %s success" % (timestamp(), self,))

    def feed_next_packet(self):
        thisi = self.i ^ 1
        data = self.inb[thisi]
        self.p.write(data, thisi)
        self.i += 1
        if self.i < TESTPACKETS:
            reactor.callLater(max(0, (len(data) / float(BPS)) - EPSILON), self.feed_next_packet)
        else:
            reactor.callLater(max(0, ((len(data) * len(self.inb)) / float(BPS)) - EPSILON), self.check_test)


class CatchupTester(Tester):
    """
    If a steady flow of TESTPACKETS packets arrives at faster than realtime, followed by a long silence, then the playout ought to play the last packet.
    """
    def check_test(self):
        self.d.callback(None)
        assert self.dml._d.b[-1] == self.inb[-1], "%s, %s" % (`self.dml._d.b[-1][:4]`, `self.inb[-1][:4]`,)
        log.msg("%s %s success" % (timestamp(), self,))

    def feed_next_packet(self):
        data = self.inb[self.i]
        self.p.write(data, self.i)
        self.i += 1
        if self.i < TESTPACKETS:
            reactor.callLater(0, self.feed_next_packet)
        else:
            reactor.callLater(max(0, ((len(data) * len(self.inb)) / float(BPS)) - EPSILON), self.check_test)

class SmoothJitterTester(Tester):
    """
    If an unstead flow arrives: two packets back-to-back followed by an "empty slot" followed by two packets back-to-back, etc., then the playout should output a perfectly even flow.
    """
    def check_test(self):
        self.d.callback(None)
        prevend = self.dml._d.ts[0] + (len(self.dml._d.b[0]) / float(BPS))
        for i in range(1, len(self.dml._d.ts)):
            ts = self.dml._d.ts[i]
            bl = len(self.dml._d.b[i])
            assert ts <= prevend, "ts: %s, prevend: %s, i: %s" % (ts, prevend, i,)
            prevend += bl / float(BPS)
        log.msg("%s %s success" % (timestamp(), self,))

    def feed_next_packet(self):
        data = str(self.i) + ('\x00' * (PACKETSIZE - len(str(self.i))))
        self.inb.append(time.time())
        self.p.write(data, self.i)
        self.i += 1
        data = str(self.i) + ('\x00' * (PACKETSIZE - len(str(self.i))))
        self.inb.append(time.time())
        self.p.write(data, self.i)
        self.i += 1
        if self.i < TESTPACKETS:
            reactor.callLater(max(0, (2 * len(data) / float(BPS)) - EPSILON), self.feed_next_packet)
        else:
            reactor.callLater(max(0, ((len(data) * len(self.inb) * 2) / float(BPS)) - EPSILON), self.check_test)


if __name__ == "__main__":
    l = []
    l.append(EvenFlowTester().d)
    l.append(CatchupTester().d)
    l.append(SmoothJitterTester().d)
    l.append(OutOfOrderArrivalTester().d)
    dl = defer.DeferredList(l)
    dl.addCallbacks(lambda x: reactor.stop(), lambda x: reactor.stop())
    reactor.run()
