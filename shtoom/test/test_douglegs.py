"Tests for the leg bridging code"
from twisted.trial import unittest

import twisted.trial.util
#twisted.trial.util.wait(testdef)

from shtoom.doug.leg import Bridge, BridgeSource

class FakeLeg:
    def _connectSource(self, source):
        self.source = source

    def read(self):
        return self.source.read()

    def write(self, bytes):
        return self.source.write(bytes)

class LegBridgingTest(unittest.TestCase):

    def testLegBridgingSimple(self):
        ae = self.assertEquals
        l1 = FakeLeg()
        l2 = FakeLeg()
        b = Bridge(leg1=l1, leg2=l2)
        l1.write('hello')
        ae(l2.read(), 'hello')
        l1.write('hello1')
        l1.write('hello2')
        ae(l2.read(), 'hello2')
        l1.write('hello3')
        l2.write('hello4')
        ae(l2.read(), 'hello3')
        ae(l1.read(), 'hello4')
