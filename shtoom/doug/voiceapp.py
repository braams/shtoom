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

class VoiceApp(StateMachine):

    def __init__(self, defer, **kwargs):
        self.__playoutList = []
        self.__recordDest = None
        self.__connected = None
        self.__currentDTMFKey = None
        self.__collectedDTMFKeys = ''
        self.__dtmfSingleMode = True
        self.__silenceSource = SilenceSource()
        self._legConnect(self.__silenceSource)
        self.__converter = DougConverter()
        super(VoiceApp, self).__init__(defer, **kwargs)

    def va_listFormats(self):
        return self.__converter.listFormats()

    def va_selectFormat(self, format, rtpPT):
        self.__rtpPT = rtpPT
        return self.__converter.selectFormat(format)

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

    def va_startDTMFevent(self, dtmf):
        c = self.__currentDTMFKey 
        if dtmf:
            if c is not dtmf:
                self.va_stopDTMFevent(c)
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
                

    def va_stopDTMFevent(self, dtmf):
        # For now, I only care about dtmf start events
        if dtmf == self.__currentDTMFKey:
            self.__currentDTMFKey = None

    def va_giveRTP(self):
        # returns (format, RTP)
        data = self.__connected.read()
        if data:
            data = self.__converter.convertOutbound(data)
            fmt = self.__rtpPT
            return fmt, data
        return None, None # comfort noise

    def va_receiveRTP(self, format, data):
        data = self.__converter.convertInbound(format, data)
        self.__connected.write(data)

    def va_start(self):
        self._start(callstart=0)

    def va_callstart(self, inboundLeg):
        self._inbound = inboundLeg
        self._triggerEvent(CallStartedEvent(inboundLeg))

    def va_callanswered(self):
        self._triggerEvent(CallAnsweredEvent(self._inbound))

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
            old.close()
            self.__recordDest = None

    def isPlaying(self):
        return self.__connected.isPlaying()

    def isRecording(self):
        return self.__connected.isRecording()

    def dtmfMode(self, single=False, timeout=0):
        self.__dtmfSingleMode = single
        # XXX handle timeout

