# Copyright (C) 2004 Anthony Baxter
"""Tests for shtoom.upnp
"""

# This is more a functional test than a unit test. oh well.

from twisted.trial import unittest
from twisted.trial import util
from twisted.internet import reactor, defer
from twisted.internet.protocol import Protocol, Factory, DatagramProtocol

import random

def checkUPnP():
    from shtoom.upnp import getUPnP
    d = getUPnP()
    s = Saver()
    d.addCallback(s.save)
    util.wait(d, timeout=8)
    if s.val is None:
        raise unittest.SkipTest('no UPnP available')

class TestUPnP:

    def discovered(self, prot):
        #print "upnp discovery done,", prot
        self.prot = prot
        return self.prot.getExternalIPAddress()

    def gotexternal(self, res):
        #print "upnp external address,",res
        return self.prot.getPortMappings()

    def gotmappings(self, res):
        #print "upnp mappings:", res
        return self.prot.addPortMapping(12367,12367,'test mapping')

    def added(self, res):
        #print "upnp port mapping added"
        return self.prot.getPortMappings()

    def gotmappings2(self, res):
        #print "upnp mappings:", res
        return self.prot.deletePortMapping(12367)

    def deleted(self, res):
        #print "upnp port mapping removed"
        return self.prot.getPortMappings()

    def gotmappings3(self, res):
        #print "upnp mappings:", res
        return self.prot.getExternalIPAddress()

    def gotexternal2(self, res):
        #print "upnp external address,",res
        pass

    def go(self):
        from shtoom.upnp import getUPnP
        d = getUPnP()
        d.addCallback(self.discovered)
        d.addCallback(self.gotexternal)
        d.addCallback(self.gotmappings)
        d.addCallback(self.added)
        d.addCallback(self.gotmappings2)
        d.addCallback(self.deleted)
        d.addCallback(self.gotmappings3)
        d.addCallback(self.gotexternal2)
        return d

class Saver:
    def __init__(self):
        self.val = None
    def save(self, val):
        self.val = val

class TestMapper:
    def __init__(self, mapper, port):
        self.port = port
        self.mapper = mapper
    def go(self):
        #print "going"
        cd = defer.Deferred()
        d = self.mapper.map(self.port)
        d.addCallback(lambda x: self.cb_mapped(x, cd))
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

class UPnPTest(unittest.TestCase):


    def test_upnp(self):
        checkUPnP()
        test = TestUPnP()
        d = test.go()
        util.wait(d, timeout=32)

    def test_upnp_mapper(self):
        from shtoom.upnp import UPnPMapper
        ae = self.assertEquals
        ar = self.assertRaises
        checkUPnP()
        mapper = UPnPMapper()
        uprot = DatagramProtocol()
        uport = reactor.listenUDP(random.randint(10000,20000), uprot)
        class tfactory(Factory):
            protocol = Protocol
        tport = reactor.listenTCP(0, tfactory())
        for port in uport, tport:
            ar(ValueError, mapper.unmap, port)
            ar(ValueError, mapper.info, port)
            t = TestMapper(mapper, port)
            d = t.go()
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
