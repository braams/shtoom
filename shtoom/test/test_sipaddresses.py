# Copyright (C) 2004 Anthony Baxter
"""Tests for SIP address parsing
"""

from twisted.trial import unittest

from twisted.protocols import sip as tpsip
from shtoom import sip as shsip


class AddressParsingTests(unittest.TestCase):
    def testParsingAndFormatting(self):
        addrs = [ '"anthony" <sip:anthony@ekit-inc.com>;tag=03860126',
                  'sip:96748002@gw2;tag=3409638C-1B50',
                  'sip:foo@bar.com',
                  'sip:foo@bar.com;tag=01234567',
                ]
        ae = self.assertEquals
        for addr in addrs:
            ae(addr, shsip.formatAddress(tpsip.parseAddress(addr)))

    def testAddressClass(self):
        addrs = [ '"anthony" <sip:anthony@ekit-inc.com>;tag=03860126',
                  'sip:96748002@gw2;tag=3409638C-1B50',
                  'sip:foo@bar.com',
                  '"foo bar" <sip:foo@bar.com>',
                  'sip:foo@bar.com;tag=01234567',
                ]
        ae = self.assertEquals
        for addr in addrs:
            ae(addr, str(shsip.Address(addr)))
        addr = shsip.Address(('anthony', 'sip:anthony@ekit-inc.com', {'tag':'03860126',}))
        ae(str(addr), '"anthony" <sip:anthony@ekit-inc.com>;tag=03860126')
        addr1 = shsip.Address(('anthony', 'sip:anthony@ekit-inc.com', {}), ensureTag=False)
        addr2 = shsip.Address('"anthony" <sip:anthony@ekit-inc.com>', ensureTag=False)
        ae(str(addr1), '"anthony" <sip:anthony@ekit-inc.com>')
        ae(str(addr1), str(addr2))
        addr = shsip.Address('"anthony" <sip:anthony@ekit-inc.com>', ensureTag=True)
        d,u,p = tpsip.parseAddress(str(addr))
        ae(p.has_key('tag'), True)
        ae(str(shsip.Address('sip:foo@bar.com')),
           str(shsip.Address(('', 'sip:foo@bar.com', {}))))
