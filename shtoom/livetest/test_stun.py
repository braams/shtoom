# Copyright (C) 2004 Anthony Baxter
"""Tests for STUN.

You can run this with command-line:

  $ trial shtoom.test.test_stun
"""

from twisted.trial import unittest, util
from twisted.internet import defer, reactor
from twisted.internet.protocol import Factory, Protocol, DatagramProtocol

class Saver:
    def save(self, arg):
        self.arg = arg

class NetAddressTests(unittest.TestCase):

    def testNetAddressInit(self):
        from shtoom.stun import NetAddress
        ae = self.assertEquals
        ar = self.assertRaises
        n1 = NetAddress('10/8')
        n2 = NetAddress('10.0.0.0/8')
        ae((n1.net,n1.mask), (n2.net, n2.mask))
        n1 = NetAddress('10.1.2.3/32')
        n2 = NetAddress('10.1.2.3')
        ae((n1.net,n1.mask), (n2.net, n2.mask))
        n1 = NetAddress('10.1.2.3/32')
        n2 = NetAddress('10.1.2.4')
        ae((n1.net+1,n1.mask), (n2.net, n2.mask))
        ar(ValueError, NetAddress, '10.1.2.3/32/3')
        ar(ValueError, NetAddress, '10.1.2.3/33')

    def testNetAddressMembership(self):
        from shtoom.stun import NetAddress
        ae = self.assertEquals
        ar = self.assertRaises
        n1 = NetAddress('10/8')
        ae(n1.check('10.1.2.3'), True)
        ae(n1.check('10.0'), True)
        ae(n1.check('10.0.0.0'), True)
        ae('10.1.2.3' in n1, True)
        ae('10.0.0.0' in n1, True)
        ae(n1.check('10.255.255.255'), True)
        ae(n1.check('10.2'), True)
        ae(n1.check('11.0'), False)
        ae(n1.check('9.255.255.255'), False)
        ae(n1.check('255.255.255.255'), False)
        n2 = NetAddress('172.16/12')
        ae(n2.check('172.16.0.0'), True)
        ae(n2.check('172.31.255.255'), True)
        ae(n2.check('172.20.10.200'), True)
        ae(n2.check('172.32.0.0'), False)
        ae(n2.check('172.15.255.255'), False)
        ae(NetAddress('172.20/16') in n2, True)
        ae(NetAddress('172.20.1.2/16') in n2, True)
        ae(NetAddress('172.16/12') in n2, True)
        ae(NetAddress('172.0/8') in n2, False)
        n3 = NetAddress('224.255.0.0')
        ae(n3.check('224.255.0.0'), True)
        ae(n3.check('224.255.0.1'), False)
        ae(n3.check('224.254.255.255'), False)
        n4 = NetAddress('0/0')
        ae(n4.check('10.0.0.0'), True)
        ae(n4.check('172.20.10.200'), True)
        ae(n4.check('224.255.0.1'), True)

    def test_stundiscovery(self):
        from shtoom.stun import getSTUN, _NatType
        ae = self.assertEquals
        a_ = self.assert_
        d = getSTUN()
        s = Saver()
        d.addCallback(s.save)
        util.wait(d, timeout=16)
        a_(isinstance(s.arg, _NatType), "%s, %s :: %s" % (s, s.arg, type(s.arg),))
