from twisted.trial import unittest


def decoratedLWCTest(IBar, b2):
    from shtoom.lwc import arguments

    @arguments(IBar)
    def takesABar(bar):
        return bar is b2

    return takesABar

# Copyright (C) 2004 Anthony Baxter

"""Tests for shtoom.defcache.
"""

from twisted.internet import defer

from shtoom.defcache import DeferredCache

class Dectest:
    @DeferredCache(inProgressOnly=False)
    def foo(self, *args):
        return defer.succeed(args)
    @DeferredCache(inProgressOnly=True, hashableArgs=True)
    def foo2(self, *args):
        return defer.succeed(args)
    @DeferredCache
    def foo3(self, *args):
        return defer.succeed(args)
