# Copyright (C) 2004 Anthony Baxter
"""Tests for shtoom.app.
"""

from twisted.trial import unittest

class TestUI:
    def statusMessage(self, mess):
        # mess
        pass

class TestAudio:
    pass

class AppStartup(unittest.TestCase):


    def buildPhone(self):
        ui = TestUI()
        audio = TestAudio()
        from shtoom.app.phone import Phone
        p = Phone(ui, audio)
        # Disable the NAT Mapping code for these tests
        p._NATMapping = False
        return p

    def getMinimalOptions(self):
        from shtoom.Options import AllOptions, OptionGroup, \
                StringOption, NumberOption, BooleanOption
        o = AllOptions()
        o.no_config_file = True
        g = OptionGroup('whatever', 'some settings')
        g.add(StringOption('ui', 'whatever', 'tk'))
        g.add(BooleanOption('no_config_file', 'whatever', True))
        g.add(StringOption('logfile', 'whatever', ''))
        g.add(NumberOption('listenport', 'port', 0))
        o.add(g)
        return o

    def test_phoneBootWithOptions(self):
        opts = self.getMinimalOptions()
        ae = self.assertEqual
        p = self.buildPhone()
        p.boot(options=opts, args=[])
        p.stopSIP()
        ae(p.getOptions(), opts)
        ae(p.getPref('ui'), 'tk')

    def test_phoneBootOpenSIP(self):
        ae = self.assertEqual
        import random
        opts = self.getMinimalOptions()
        l=random.randint(20000,30000)
        ae = self.assertEqual
        p = self.buildPhone()
        p.boot(options=opts, args=['--listenport=%d'%l])
        ae(opts.getValue('listenport'), l)
        ae(p.sipListener.port, p.getPref('listenport'))
        p.stopSIP()
