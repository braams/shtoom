# Copyright (C) 2004 Anthony Baxter

"""Tests for shtoom.defcache.
"""

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

