# Copyright (C) 2004 Anthony Baxter
"""Tests for SIP address parsing
"""

from twisted.trial import unittest

from twisted.protocols import sip as tpsip
from shtoom import sip as shsip


class DialogTests(unittest.TestCase):
    def testDialogCtor(self):
        from shtoom.sip import Dialog, Address
        ae = self.assertEquals

        addr1 = '"anthony" <sip:anthony@ekit-inc.com>;tag=03860126'
        addr2 = 'sip:96748002@gw2;tag=3409638C-1B50'
        Addr1 = Address(addr1)
        Addr2 = Address(addr2)

        d = Dialog()
        d.setCaller(addr1)
        d.setCallee(addr2)
        ae(d.getCaller().__class__, Address)
        ae(str(d.getCaller()), addr1)
        ae(str(d.getCallee()), addr2)
        d.setCaller(Addr1)
        d.setCallee(Addr2)
        ae(d.getCaller(), Addr1)
        ae(d.getCallee(), Addr2)
        d.setDirection(inbound=True)
        ae(d.getRemoteTag(), Addr1)
        ae(d.getLocalTag(), Addr2)
        d.setDirection(outbound=True)
        ae(d.getLocalTag(), Addr1)
        ae(d.getRemoteTag(), Addr2)
