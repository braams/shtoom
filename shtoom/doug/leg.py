# Copyright (C) 2004 Anthony Baxter

""" A leg """


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

    def incomingCall(self, d):
        " This leg is an incoming call "
        self._acceptDeferred = d

    def getVoiceApp(self):
        "Get the VoiceApp currently connected to this leg"
        return self._voiceapp

    def hijackLeg(self, voiceapp):
        """ Remove the currently running VoiceApp from the leg, and
            slot in a new one. Returns the hijacked app.
        """
        old, self._voiceapp = self._voiceapp, voiceapp
        return old

    def answerCall(self, voiceapp):
        " Answer the call on this leg "
        print "answering this call", self
        if self._acceptDeferred is not None:
            self._voiceapp = voiceapp
            d, self._acceptDeferred = self._acceptDeferred, None
            d.callback(self._cookie)
        else:
            log.msg("can't reject call %s, already answered/rejected"%(self.cookie))

    def rejectCall(self, reason):
        " Reject the call on this leg "
        if self._acceptDeferred is not None:
            d, self._acceptDeferred = self._acceptDeferred, None
            self._voiceapp = None
            self._cookie = None
            d.errback(reason)
        else:
            log.msg("can't reject call %s, already answered/rejected"%(self.cookie))
    
