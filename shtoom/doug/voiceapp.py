# Copyright (C) 2004 Anthony Baxter

""" VoiceApp base class

    This is just a first cut at the VoiceApp. Do NOT assume that
    the interfaces here won't be entirely rewritten in the future.

    In fact, ASSUME that they will be rewritten entirely. Repeatedly.

"""

from shtoom.doug.source import SilenceSource, convertToSource
from shtoom.doug.events import *
from shtoom.doug.exceptions import *
from shtoom.doug.statemachine import StateMachine
from twisted.internet import reactor
from shtoom.audio.converters import DougConverter

try:
    import numarray
except ImportError:
    numarray = None

if numarray is not None:
    class InbandDtmfDetector:
        def __init__(self, voiceapp):
            from shtoom.doug.dtmfdetect import DtmfDetector
            self.voiceapp = voiceapp
            self.prev = None
            self.D = DtmfDetector()
            self.digit = ''
        def __call__(self, samp):
            if self.prev is None:
                self.prev = samp
                return
            nd = self.D.detect(self.prev+samp)
            if nd != self.digit:
                if self.digit == '':
                    self.digit = nd
                    self.voiceapp.va_startDTMFevent(nd)
                elif nd == '':
                    old, self.digit = self.digit, nd
                    self.voiceapp.va_stopDTMFevent(old)
                else:
                    old, self.digit = nd, self.digit
                    self.voiceapp.va_stopDTMFevent(old)
                    self.voiceapp.va_startDTMFevent(self.digit)
            self.prev = samp

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

    def __init__(self, defer, appl, cookie, **kwargs):
        self.__playoutList = []
        self.__cookie = cookie
        self.__recordDest = None
        self.__connected = None
        self.__currentDTMFKey = None
        self.__collectedDTMFKeys = ''
        self.__dtmfSingleMode = True
        self.__silenceSource = SilenceSource()
        self._legConnect(self.__silenceSource)
        self.__converter = DougConverter()
        self.__appl = appl
        self.__inbandDTMFdetector = None
        super(VoiceApp, self).__init__(defer, **kwargs)

    def va_selectDefaultFormat(self, ptlist, callcookie):
        return self.__converter.selectDefaultFormat(ptlist)

    def _legConnect(self, target):
        target.app = self
        old, self.__connected = self.__connected, target
        if old:
            old.app = None
        return old

    def _va_playNextItem(self):
        if not self.__playoutList:
            last = self._legConnect(self.__silenceSource)
            self._triggerEvent(MediaPlayContentDoneEvent(last))
        else:
            next = self.__playoutList.pop(0)
            next = convertToSource(next, 'r')
            self._legConnect(next)

    def _va_maybeStartPlaying(self):
        # If we're not already playing, switch out the silence
        if self.__connected is self.__silenceSource:
            self._va_playNextItem()

    def _va_sourceDone(self, source):
        if self.__connected is source:
            self._va_playNextItem()

    def va_startDTMFevent(self, dtmf, callcookie):
        c = self.__currentDTMFKey
        if dtmf:
            if c is not dtmf:
                self.va_stopDTMFevent(c, callcookie)
                self.__currentDTMFKey = dtmf
                self._inboundDTMFKeyPress(dtmf)
            else:
                # repeat
                pass

    def _inboundDTMFKeyPress(self, dtmf):
        if self.__dtmfSingleMode:
            self._triggerEvent(DTMFReceivedEvent(dtmf))
        else:
            self.__collectedDTMFKeys += dtmf
            if dtmf in ('#', '*'):
                dtmf, self.__collectedDTMFKeys = self.__collectedDTMFKeys, ''
                self._triggerEvent(DTMFReceivedEvent(dtmf))


    def va_stopDTMFevent(self, dtmf, callcookie):
        # For now, I only care about dtmf start events
        if dtmf == self.__currentDTMFKey:
            self.__currentDTMFKey = None

    def va_giveRTP(self, callcookie):
        # returns (format, RTP)
        data = self.__connected.read()
        if data:
            packet = self.__converter.convertOutbound(data)
            return packet
        return None # comfort noise

    def va_receiveRTP(self, packet, callcookie):
        data = self.__converter.convertInbound(packet)
        if self.__inbandDTMFdetector is not None:
            self.__inbandDTMFdetector(data)
        self.__connected.write(data)

    def va_start(self):
        self._start(callstart=0)

    def va_callstart(self, inboundLeg):
        self._inbound = inboundLeg
        self._triggerEvent(CallStartedEvent(inboundLeg))

    def va_callanswered(self, leg=None):
        if leg is None:
            leg = self._inbound
        self._triggerEvent(CallAnsweredEvent(leg))

    def va_callrejected(self, leg=None):
        if leg is None:
            leg = self._inbound
        self._triggerEvent(CallRejectedEvent(leg))

    def va_abort(self):
        self.mediaStop()
        self._triggerEvent(CallEndedEvent(None))

    def mediaPlay(self, playlist):
        if isinstance(playlist, basestring):
            playlist = [playlist]
        self.__playoutList.extend(playlist)
        self._va_maybeStartPlaying()

    def mediaRecord(self, dest):
        dest = convertToSource(dest, 'w')
        self._legConnect(dest)

    def mediaStop(self):
        old = self._legConnect(self.__silenceSource)
        if old.isPlaying():
            old.close()
            self.__playoutList = []
            if old.isRecording():
                self.__recordDest = None
        elif old.isRecording():
            old.close()
            self.__recordDest = None

    def setTimer(self, delay):
        return Timer(self, delay)

    def isPlaying(self):
        return self.__connected.isPlaying()

    def isRecording(self):
        return self.__connected.isRecording()

    def dtmfMode(self, single=False, inband=False, timeout=0):
        self.__dtmfSingleMode = single
        if inband:
            if numarray is False:
                raise RuntimeError, "need numarray to do inband DTMF"
            else:
                self.__inbandDTMFdetector = InbandDtmfDetector(self)
        else:
            self.__inbandDTMFdetector = None
        # XXX handle timeout

    def placeCall(self, toURI, fromURI=None):
        self.__appl.placeCall(self.__cookie, toURI, fromURI)

    def va_hangupCall(self, cookie):
        self.__appl.dropCall(cookie)

    def connectLeg(self, leg1, leg2=None):
        if leg2 is None:
            self._inbound = leg1
        else:
            raise NotImplementedError, "can't connect legs yet"

    def sendDTMF(self, digits, cookie=None, duration=0.1, delay=0.05):
        "Send a string of DTMF keystrokes"
        for n,key in enumerate(digits):
            if key not in '01234567890#*':
                raise ValueError, key
            n = float(n) # just in case
            if cookie is None:
                cookie = self.__cookie
            i = 0.2
            reactor.callLater(i+n*(duration+delay),
                lambda k=key: self.__appl.startDTMF(cookie, k))
            reactor.callLater(i+n*(duration+delay)+duration,
                lambda k=key: self.__appl.stopDTMF(cookie, k))
