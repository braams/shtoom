"Tests for the leg bridging code"
from twisted.trial import unittest
import twisted.trial.util
from twisted.internet import defer

from shtoom.doug.leg import Bridge, BridgeSource, Leg

class FakeLegForBridging:
    def _connectSource(self, source):
        source.leg = self
        self.source = source

    def _sourceDone(self, source):
        self.source = None

    def mediaStop(self):
        self.source.close()

    def read(self):
        return self.source.read()

    def write(self, bytes):
        return self.source.write(bytes)

class DougLegTests(unittest.TestCase):

    def testLegBridgingSimple(self):
        ae = self.assertEquals
        l1 = FakeLegForBridging()
        l2 = FakeLegForBridging()
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
        l1.mediaStop()
        ae(l1.source, None)
        ae(l2.source, None)

    def test_legConstructor(self):
        from shtoom.sip import Dialog
        ae = self.assertEquals
        d = Dialog()
        cookie = 'NCookie'
        l = Leg(cookie, d)
        ae(l.getCookie(), cookie)
        ae(l.getDialog(), d)
        l.setCookie('foo')
        ae(l.getCookie(), 'foo')
        # We should be connected to silence at this point
        class Foo:
            def handle_media_sample(self, sample, tester=self):
                tester.fail("WRONG.  We should be hearing silence, but we received this sample: %s" % (sample,))
        l.set_handler(Foo())

    def test_legCallSetup(self):
        from shtoom.sip import Dialog
        ae = self.assertEquals
        d = Dialog()
        cookie = 'NCookie'
        class A:
            res = None
            def good(self, res):
                self.res = res
            def bad(self, err):
                self.res = err

        l = Leg(cookie, d)
        a = A()
        d = defer.Deferred()
        d.addCallbacks(a.good, a.bad)
        l.incomingCall(d)
        ae(a.res, None)
        l.answerCall(voiceapp=None)
        twisted.trial.util.wait(d)
        ae(a.res, cookie)
        l.rejectCall(Exception('because'))
        twisted.trial.util.wait(d)
        ae(a.res, cookie)

        l = Leg(cookie, d)
        a = A()
        d = defer.Deferred()
        d.addCallbacks(a.good, a.bad)
        l.incomingCall(d)
        ae(a.res, None)
        # XXX should be an exception
        l.rejectCall(Exception('because'))
        twisted.trial.util.wait(d)
        # rejectCall triggers an errback, so we get
        # Failure(DefaultException(reason))
        ae(a.res.value.args, ('because',))
