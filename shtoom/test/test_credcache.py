# Copyright (C) 2004 Anthony Baxter
"""Tests for shtoom.credcache
"""

from twisted.trial import unittest
from shtoom.Options import OptionDict, AllOptions

from shtoom.credcache import CredCache

class DummyApp:
    def __init__(self):
        self.all = AllOptions()
        self.creds = OptionDict('credentials', 'credentials')
        self.all.addGroup(self.creds)
        self.ini = None

    def getPref(self, name):
        if name == "credentials":
            return self.creds
        else:
            raise NameError(name)

    def updateOptions(self, dict, forceSave=False):
        if forceSave:
            self.ini = self.all.emitConfigParser()

class CredCacheTests(unittest.TestCase):

    def test_credcache_set_save(self):
        ae = self.assertEquals
        app = DummyApp()
        c = CredCache(app)
        ae(c.getCred('sip.foo.com'), None)
        c.addCred('sip.foo.com', 'gonzo', 'seekrit')
        ae(c.getCred('sip.foo.com'), ('gonzo', 'seekrit'))
        c.addCred('sip.bar.com', 'gazpacho', 'soup', save=True)
        ae(c.getCred('sip.bar.com'), ('gazpacho', 'soup'))
        ae(app.ini, '[credentials]\nsip.bar.com=Z2F6cGFjaG8Ac291cA==\n')
        c.addCred('sip.bar.com', 'gazpacho', 'bowl', save=True)
        ae(c.getCred('sip.bar.com'), ('gazpacho', 'bowl'))
        ae(app.ini, '[credentials]\nsip.bar.com=Z2F6cGFjaG8AYm93bA==\n')
        c.addCred('sip.foo.com', 'gonzo', 'seekrit', save=True)
        ae(app.ini, '[credentials]\nsip.foo.com=Z29uem8Ac2Vla3JpdA==\nsip.bar.com=Z2F6cGFjaG8AYm93bA==\n')

    def test_credcache_load(self):
        from StringIO import StringIO
        ae = self.assertEquals
        app = DummyApp()
        c = CredCache(app)
        s = StringIO()
        s.write('[credentials]\nsip.foo.com=Z29uem8Ac2Vla3JpdA==\nsip.bar.com=Z2F6cGFjaG8AYm93bA==\n')
        s.seek(0)
        app.all.loadOptsFile(s)
        c.loadCreds(app.creds)
        ae(c.getCred('sip.bar.com'), ('gazpacho', 'bowl'))
        ae(c.getCred('sip.foo.com'), ('gonzo', 'seekrit'))
