# Copyright (C) 2004 Anthony Baxter
"""Tests for shtoom.nat and friends
"""

# This is more a functional test than a unit test. oh well.

from twisted.trial import unittest
from twisted.trial import util
from twisted.internet import reactor, defer
from twisted.internet.protocol import Protocol, Factory, DatagramProtocol

from shtoom.livetest.test_upnp import checkUPnP

import random

def logerr(failure):
    print "logerr", failure
    print failure.value
    return failure

class TestMapper:
    def __init__(self, mapper, port):
        self.port = port
        self.mapper = mapper

    def go(self):
        #print "going"
        cd = defer.Deferred()
        d = self.mapper.map(self.port)
        d.addCallback(lambda x: self.cb_mapped(x, cd)).addErrback(logerr)
        return cd

    def cb_mapped(self, ext, cd):
        #print "mapped"
        self.map_res = ext
        self.info_res = self.mapper.info(self.port)
        d = self.mapper.unmap(self.port)
        d.addCallback(lambda x: self.cb_unmapped(x, cd))

    def cb_unmapped(self, res, cd):
        #print "unmapped"
        self.unmap_res = res
        cd.callback(None)

class Saver:
    def save(self, arg):
        self.arg = arg


class MapperTest(unittest.TestCase):

    def tearDown(self):
        import shtoom.nat
        shtoom.nat.clearCache()

    def test_upnp_mapper(self):
        from shtoom.upnp import UPnPMapper
        ae = self.assertEquals
        ar = self.assertRaises
        checkUPnP()
        mapper = UPnPMapper()
        uprot = DatagramProtocol()
        uport = reactor.listenUDP(random.randint(10000,26000), uprot)
        class tfactory(Factory):
            protocol = Protocol
        tport = reactor.listenTCP(0, tfactory())
        for port in uport, tport:
            ar(ValueError, mapper.unmap, port)
            ar(ValueError, mapper.info, port)
            t = TestMapper(mapper, port)
            d = t.go()
            d.addErrback(logerr)
            util.wait(d, timeout=16)
            ae(len(t.map_res), 2)
            ae(t.map_res, t.info_res)
            ae(t.unmap_res, None)
            # Can't unmap a port that's not mapped
            ar(ValueError, mapper.unmap, port)
            d = port.stopListening()
            util.wait(d)
            # Can't map a closed port
            ar(ValueError, mapper.map, port)
            # Can't get info on a closed port
            ar(ValueError, mapper.info, port)

    def test_stunmapper(self):
        from shtoom.stun import getSTUN, STUNMapper
        ae = self.assertEquals
        ar = self.assertRaises

        d = getSTUN()
        s = Saver()
        d.addCallback(s.save)
        util.wait(d, timeout=64)
        if not s.arg.useful:
            raise unittest.SkipTest('No useful STUN')

        mapper = STUNMapper()
        # Check we have a hate-on for TCP ports
        class tfactory(Factory):
            protocol = Protocol
        tport = reactor.listenTCP(0, tfactory())
        ar(ValueError, mapper.map, tport)
        tport.stopListening()
        ar(ValueError, mapper.map, tport)

        prot = DatagramProtocol()
        port = reactor.listenUDP(0, prot)
        ar(ValueError, mapper.info, port)
        t = TestMapper(mapper, port)
        d = t.go()
        util.wait(d, timeout=512)
        ae(len(t.map_res), 2)
        ae(t.map_res, t.info_res)
        ae(t.unmap_res, None)
        d = port.stopListening()
        util.wait(d)
        ar(ValueError, mapper.map, port)
        ar(ValueError, mapper.info, port)

    def test_nullmapper(self):
        from shtoom.nat import getNullMapper
        mapper = getNullMapper()
        ae = self.assertEquals
        ar = self.assertRaises
        uprot = DatagramProtocol()
        uport = reactor.listenUDP(0, uprot)
        class tfactory(Factory):
            protocol = Protocol
        tport = reactor.listenTCP(0, tfactory())
        for port in uport, tport:
            ar(ValueError, mapper.unmap, port)
            ar(ValueError, mapper.info, port)
            t = TestMapper(mapper, port)
            d = t.go()
            util.wait(d)
            ae(len(t.map_res), 2)
            ae(t.map_res, t.info_res)
            ae(t.unmap_res, None)
            # Can't unmap a port that's not mapped
            ar(ValueError, mapper.unmap, port)
            d = port.stopListening()
            util.wait(d)
            # Can't map a closed port
            ar(ValueError, mapper.map, port)
            # Can't get info on a closed port
            ar(ValueError, mapper.info, port)
