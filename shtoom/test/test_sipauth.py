# Copyright (C) 2004 Anthony Baxter
"""Tests for shtoom.app.
"""

from twisted.trial import unittest

class AuthTest(unittest.TestCase):

    def test_sipSimpleAuth(self):
        from shtoom.sip import Registration
        reg = Registration(None, None)
        resp = reg.calcAuth('REGISTER', 'sip:divmod.com',
                     'Digest realm="asterisk", nonce="24a52b3a"',
                     ('anthony', 'foo'))
        correct = 'Digest username="anthony",realm="asterisk",nonce="24a52b3a",response="925bd204843bf802a1ed8a2494557c01",uri="sip:divmod.com"'
        correct = correct.split(',')
        correct = [ x.strip() for x in correct ]
        correct.sort()
        resp = resp.split(',')
        resp = [ x.strip() for x in resp ]
        resp.sort()
        self.assertEqual(resp, correct)
