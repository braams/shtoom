# Copyright (C) 2004 Anthony Baxter

""" VoiceApp base class

    This is just a first cut at the VoiceApp. Do NOT assume that
    the interfaces here won't be entirely rewritten in the future.

    In fact, ASSUME that they will be rewritten entirely. Repeatedly.

"""

from shtoom.doug.events import *
from shtoom.doug.exceptions import *
from shtoom.doug.statemachine import StateMachine
from twisted.internet import reactor
from twisted.python.util import OrderedDict
from twisted.python import log

class Timer:
    def __init__(self, voiceapp, delay):
        self._delay = delay
        self._voiceapp = voiceapp
        self._timer = reactor.callLater(delay, self._trigger)

    def _trigger(self):
        v, self._voiceapp = self._voiceapp, None
        v._triggerEvent(TimeoutEvent(self))

    def cancel(self):
        self._timer.cancel()
        self._voicapp = None

class VoiceApp(StateMachine):

    _inbound = None

    def __init__(self, defer, appl, cookie, **kwargs):
        self.__cookie = cookie
        self.__appl = appl
        self.__legs = OrderedDict()
        self.__dict__.update(kwargs)
        super(VoiceApp, self).__init__(defer, **kwargs)

    def getDefaultLeg(self):
        return self.__legs.values()[0]

    def getLeg(self, cookie):
        return self.__legs.get(cookie)

    def setLeg(self, leg, cookie):
        self.__legs[cookie] = leg

    def va_selectDefaultFormat(self, ptlist, callcookie):
        return self.getLeg(callcookie).selectDefaultFormat(ptlist)

    def va_receiveRTP(self, packet, callcookie):
        return self.getLeg(callcookie).leg_receiveRTP(packet)

    def va_start(self):
        self._start(callstart=0)

    def va_callstart(self, inboundLeg):
        if inboundLeg is not None:
            self.__legs[inboundLeg.getCookie()] = inboundLeg
            if self._inbound is None:
                self._inbound = inboundLeg
        self._triggerEvent(CallStartedEvent(inboundLeg))

    def va_callanswered(self, leg=None):
        if leg is None:
            leg = self._inbound
        self._triggerEvent(CallAnsweredEvent(leg))

    def va_callrejected(self, leg=None):
        if leg is None:
            leg = self._inbound
        try:
            del self.__legs[leg]
        except KeyError:
            log.msg("can't find leg %s, current legs: %r"%(
                                    leg, self.__legs.keys()),
                                    system='doug')
        self._triggerEvent(CallRejectedEvent(leg))

    def va_abort(self):
        self.mediaStop()
        self._triggerEvent(CallEndedEvent(None))

    def mediaPlay(self, playlist, leg=None):
        if leg is None:
            leg = self.getDefaultLeg()
        leg.mediaPlay(playlist)

    def mediaRecord(self, dest, leg=None):
        if leg is None:
            leg = self.getDefaultLeg()
        leg.mediaRecord(dest)

    def mediaStop(self, leg=None):
        if leg is None:
            leg = self.getDefaultLeg()
        leg.mediaStop()

    def setTimer(self, delay):
        return Timer(self, delay)

    def isPlaying(self, leg=None):
        if leg is None:
            leg = self.getDefaultLeg()
        return leg.isPlaying()

    def isRecording(self, leg=None):
        if leg is None:
            leg = self.getDefaultLeg()
        return leg.isRecording()

    def dtmfMode(self, single=False, inband=False, timeout=0, leg=None):
        if leg is None:
            leg = self.getDefaultLeg()
        leg.dtmfMode(single, inband, timeout)

    def placeCall(self, toURI, fromURI=None):
        from shtoom.doug.leg import Leg
        nleg = Leg(cookie=None, dialog=None)
        self.__appl.placeCall(self.__cookie, nleg, toURI, fromURI)

    def va_hangupCall(self, cookie):
        self.__appl.dropCall(cookie)

    def connectLegs(self, leg1, leg2=None):
        from shtoom.doug.leg import Bridge

        if leg2 is None:
            leg2 = self.getDefaultLeg()
        if leg1 is leg2:
            raise ValueError, "can't join %r to itself!"%(leg1)
        else:
            b = Bridge(leg1, leg2)
            return b

    def sendDTMF(self, digits, cookie=None, duration=0.1, delay=0.05):
        "Send a string of DTMF keystrokes"
        for n,key in enumerate(digits):
            if key not in ',01234567890#*':
                raise ValueError, key
            if key == ',':
                # pause
                continue
            n = float(n) # just in case
            if cookie is None:
                cookie = self.__cookie
            i = 0.2
            reactor.callLater(i+n*(duration+delay),
                lambda k=key: self.__appl.startDTMF(cookie, k))
            reactor.callLater(i+n*(duration+delay)+duration,
                lambda k=key: self.__appl.stopDTMF(cookie, k))
