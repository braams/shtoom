# Copyright (C) 2004 Anthony Baxter

"""
    A Leg is a SIP connection from one UA to another UA. A typical
    voiceapp might have only one Leg (for the incoming SIP call),
    it might have two (an incoming and an outgoing leg that are
    connected, or 'conferenced' together, for instance) or indeed
    many legs (for some more exotic use-case).
"""

from shtoom.doug.source import Source
from shtoom.doug.events import CallAnsweredEvent, CallRejectedEvent
from twisted.python import log

class Leg(object):

    _dialog = None
    _cookie = None
    _acceptDeferred = None
    _voiceapp = None

    def __init__(self, cookie, dialog):
        """ Create a new leg
        """
        self._cookie = cookie
        self._dialog = dialog
        self._acceptDeferred = None

    def getDialog(self):
        return self._dialog

    def getCookie(self):
        return self._cookie

    def incomingCall(self, d):
        " This leg is an incoming call "
        self._acceptDeferred = d

    def outgoingCall(self):
        " This leg is an outgoing call "
        pass

    def getVoiceApp(self):
        "Get the VoiceApp currently connected to this leg"
        return self._voiceapp

    def hijackLeg(self, voiceapp):
        """ Remove the currently running VoiceApp from the leg, and
            slot in a new one. Returns the hijacked app.
        """
        old, self._voiceapp = self._voiceapp, voiceapp
        return old

    def callAnswered(self, voiceapp):
        "Called when an outbound call is answered"
        self._voiceapp = voiceapp
        voiceapp._triggerEvent(CallAnsweredEvent(self))

    def callRejected(self, voiceapp):
        "Called when an outbound call is rejected"
        self._voiceapp = voiceapp
        voiceapp._triggerEvent(CallRejectedEvent(self))

    def answerCall(self, voiceapp):
        " Answer the (incoming) call on this leg "
        print "answering this call", self
        if self._acceptDeferred is not None:
            self._voiceapp = voiceapp
            d, self._acceptDeferred = self._acceptDeferred, None
            d.callback(self._cookie)
        else:
            log.msg("can't answer call %s, already answered/rejected"%(
                                                self._cookie), system='doug')

    def rejectCall(self, reason):
        " Reject the (incoming) call on this leg "
        if self._acceptDeferred is not None:
            d, self._acceptDeferred = self._acceptDeferred, None
            self._voiceapp = None
            self._cookie = None
            d.errback(reason)
        else:
            log.msg("can't reject call %s, already answered/rejected"%(
                                                self._cookie), system='doug')

    def hangupCall(self):
        self._voiceapp.va_hangupCall(self._cookie)

    def sendDTMF(self, digits, duration=0.1, delay=0.05):
        self._voiceapp.sendDTMF(digits, cookie=self._cookie,
                                duration=duration, delay=delay)

class BridgeSource(Source):
    "A BridgeSource connects a leg to another leg via a bridge"
    def __init__(self, app, bridge):
        self.app = app
        self.bridge = bridge
        self._readbuffer = ''

    def connect(self, other):
        self.other = other

    def isPlaying(self):
        return True

    def isRecording(self):
        return True

    def copyData(self, bytes):
        "Copy data to the other leg"
        self._readbuffer = bytes

    def read(self):
        b, self._readbuffer = self._readbuffer, ''
        return b

    def write(self, bytes):
        self.other.copyData(bytes)
    
    def close(self):
        self.bridge.closeBridge(self)
        self.other.close()

class Bridge:
    """A bridge connects two legs together, and passes audio from one to
       the other. It creates two Source objects, that are connected to
       each leg"""
    def __init__(self, app, leg1, leg2):
        self.app = app
        self.connectLegs(leg1, leg2)

    def connectLegs(self, l1, l2):
        bs1 = BridgeSource(self.app, self)
        bs2 = BridgeSource(self.app, self)
        bs1.connect(bs2)
        bs2.connect(bs1)
        l1.connectSource(bs1)
        l2.connectSource(bs2)

    def close(self, bs):
        # Nothing for now.
        pass
        
