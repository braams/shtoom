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


