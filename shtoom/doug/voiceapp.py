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

class VoiceApp(StateMachine):

    def __init__(self, defer, **kwargs):
        self._playoutList = []
        self._recordDest = None
        self._connected = None
        self._silenceSource = SilenceSource()
        self._legConnect(self._silenceSource)
        super(VoiceApp, self).__init__(defer, **kwargs)

    def _legConnect(self, target):
        target.app = self
        old, self._connected = self._connected, target
        old.app = None
        return old

    def _playNextItem(self):
        if not self._playoutList:
            self._legConnect(self._silenceSource)
            self._triggerEvent(MediaPlayContentDoneEvent)
        else:
            next = self._playoutList.pop(0)
            next = convertToSource(next, 'r')
            self._legConnect(next)

    def _maybeStartPlaying(self):
        # If we're not already playing, switch out the silence
        if self._connected is self._silenceSource:
            self._playNextItem()

    def mediaPlay(self, playlist):
        self._playoutList.extend(playlist)
        self._maybeStartPlaying()

    def mediaRecord(self, dest):
        dest = convertToSource(dest, 'w')
        self._legConnect(dest)

    def mediaStop(self):
        old = self._legConnect(self._silenceSource)
        if old.isPlaying():
            old.close()
            self._playoutList = []
        if old.isRecording():
            old.close()
            self._recordDest = None

    def isPlaying(self):
        return self._connected.isPlaying()

    def isRecording(self):
        return self._connected.isRecording()

    def dtmfMode(self, single=False, timeout=0):
        self._dtmfSingleMode = single
        # XXX handle timeout

