# Copyright (C) 2004 Anthony Baxter

"""Tests for shtoom.defcache.
"""

# XXX Todo:
#   - Test errbacks
#   - Test that errors in user callbacks don't interfere with other
#     results, and neither do deferreds returned by user callbacks
#   - More tests of the decorated versions

from twisted.trial import unittest
from shtoom.defcache import DeferredCache
from twisted.internet import defer, reactor
from twisted.trial import util

class TestBlobby:
    def __init__(self):
        self.calls = []
        self.operation = DeferredCache(self._operation, inProgressOnly=False)

    def _operation(self, *args, **kwargs):
        # Stub pointless operation - returns the first value passed,
        # after a small delay
        self.calls.append((args,kwargs))
        opdef = defer.Deferred()
        reactor.callLater(0, lambda : opdef.callback(args[0]))
        return opdef

    operation2 = DeferredCache(_operation, hashableArgs=True, inProgressOnly=False)
    operation3 = DeferredCache(_operation, inProgressOnly=True)

class Saver:
    def __init__(self):
        self.val = None

    def save(self, arg):
        #print "Saver", self, "called with", arg
        self.val = arg


class DefcacheTests(unittest.TestCase):

    def test_defcache(self):
        ae = self.assertEquals
        ar = self.assertRaises

        t = TestBlobby()
        s = Saver()
        d = t.operation('foo')
        d.addCallback(s.save)
        util.wait(d)
        ae(s.val, 'foo')

        t = TestBlobby()
        s1 = Saver()
        s2 = Saver()
        d1 = t.operation('foo')
        d2 = t.operation('foo')
        d1.addCallback(s1.save)
        d2.addCallback(s2.save)
        util.wait(d1)
        util.wait(d2)
        ae(s1.val, 'foo')
        ae(s2.val, 'foo')
        # Check it was only called once, as expected
        ae(t.calls, [(('foo',),{})])
        # Check for the cache of completed calls
        d3 = t.operation('foo')
        s3 = Saver()
        d3.addCallback(s3.save)
        util.wait(d3)
        ae(s3.val, 'foo')
        ae(t.calls, [(('foo',),{})])

        # Now test kwargs
        t = TestBlobby()
        s1 = Saver()
        s2 = Saver()
        s3 = Saver()
        d1 = t.operation('foo', kw=True)
        d2 = t.operation('foo', kw=True)
        d3 = t.operation('foo', kw=False)
        d1.addCallback(s1.save)
        d2.addCallback(s2.save)
        d3.addCallback(s3.save)
        util.wait(d1)
        util.wait(d2)
        util.wait(d3)
        ae(s1.val, 'foo')
        ae(s2.val, 'foo')
        ae(s3.val, 'foo')
        # Check it was called twice only
        ae(len(t.calls), 2)

        t = TestBlobby()
        ar(TypeError, t.operation2, 'bar', {})

        s1 = Saver()
        s2 = Saver()
        d1 = t.operation2('bar', kw=True)
        d2 = t.operation('bar', kw=True)
        d1.addCallback(s1.save)
        d2.addCallback(s2.save)
        util.wait(d1)
        util.wait(d2)
        ae(s1.val, 'bar')
        ae(s2.val, 'bar')
        # Check it was called twice only
        ae(len(t.calls), 2)

        t = TestBlobby()

        s1 = Saver()
        s2 = Saver()
        d1 = t.operation('foo', kw={})
        d2 = t.operation('foo', kw={})
        d1.addCallback(s1.save)
        d2.addCallback(s2.save)
        util.wait(d1)
        util.wait(d2)
        ae(s1.val, 'foo')
        ae(s2.val, 'foo')
        # Check it was called both times
        ae(len(t.calls), 2)

        t = TestBlobby()
        s1 = Saver()
        s2 = Saver()
        s3 = Saver()
        s4 = Saver()
        d1 = t.operation3('foo', 1, 2, 3)
        d2 = t.operation3('foo', 1, 2, 3)
        d1.addCallback(s1.save)
        d2.addCallback(s2.save)
        util.wait(d1)
        util.wait(d2)
        ae(s1.val, 'foo')
        ae(s2.val, 'foo')
        ae(len(t.calls), 1)
        d3 = t.operation3('foo', 1, 2, 3)
        d4 = t.operation3('foo', 1, 2, 3)
        d3.addCallback(s3.save)
        d4.addCallback(s4.save)
        util.wait(d3)
        util.wait(d4)
        ae(s3.val, 'foo')
        ae(s4.val, 'foo')
        ae(len(t.calls), 2)

        t = TestBlobby()
        s1 = Saver()
        s2 = Saver()
        d1 = t.operation('foo')
        d2 = t.operation('foo')
        d1.addCallback(s1.save)
        d2.addCallback(s2.save)
        util.wait(d1)
        util.wait(d2)
        ae(s1.val, 'foo')
        ae(s2.val, 'foo')
        # Check it was only called once, as expected
        ae(len(t.calls), 1)
        # Clear the cache
        t.operation.clearCache()
        d3 = t.operation('foo')
        s3 = Saver()
        d3.addCallback(s3.save)
        util.wait(d3)
        ae(s3.val, 'foo')
        ae(len(t.calls), 2)

        # Now test kwargs
        t = TestBlobby()
        s1 = Saver()
        s2 = Saver()
        s3 = Saver()
        d1 = t.operation('foo', kw=True)
        d2 = t.operation('foo', kw=True)
        d3 = t.operation('foo', kw=False)
        d1.addCallback(s1.save)
        d2.addCallback(s2.save)
        d3.addCallback(s3.save)
        util.wait(d1)
        util.wait(d2)
        util.wait(d3)
        ae(s1.val, 'foo')
        ae(s2.val, 'foo')
        ae(s3.val, 'foo')
        # Check it was called twice only
        ae(len(t.calls), 2)

    def test_decorating(self):
        import sys
        if sys.version_info < (2,4):
            raise unittest.SkipTest('decorators only available on 2.4 and later')
        ae = self.assertEquals
        ar = self.assertRaises

        # Has to be elsewhere to avoid SyntaxErrors :-(
        from shtoom.test.py24tests import Dectest

        # XXX actually test the stupid things?!
        d = Dectest()
        ae(d.foo.cache_inProgressOnly, False)
        ae(d.foo.cache_inProgressOnly, False)
        ae(d.foo2.cache_inProgressOnly, True)
        ae(d.foo3.cache_inProgressOnly, True)
        ae(d.foo3.cache_hashableArgs, False)
        ar(TypeError, d.foo2, {})
        s = Saver()
        d = d.foo(1,2,3)
        d.addCallback(s.save)
        util.wait(d)
        ae(s.val, (1,2,3))
