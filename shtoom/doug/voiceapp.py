# Copyright (C) 2004 Anthony Baxter

""" VoiceApp base class

    This is just a first cut at the VoiceApp. Do NOT assume that 
    the interfaces here won't be entirely rewritten in the future.

    In fact, ASSUME that they will be rewritten entirely. Repeatedly.

"""

from shtoom.doug.source import SilenceSource, convertToSource
from shtoom.doug.events import *
from shtoom.doug.exceptions import *

from twisted.internet import reactor

class VoiceApp(object):

    def __init__(self, defer, **kwargs):
        self._playoutList = []
        self._recordDest = None
        self._connected = None
        self._silenceSource = SilenceSource()
        self._legConnect(self._silenceSource)
        self._doneDeferred = defer

    def _legConnect(self, target):
        old, self._connected = self._connected, target
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

    def returnResult(self, result):
        d, self._doneDeferred = self._doneDeferred, None
        d.callback(result)

    def returnError(self, exc):
        d, self._doneDeferred = self._doneDeferred, None
        d.errback(exc)

    def cleanUp(self):
        # XXX keep track of stuff
        pass

    def __start__(self):
        raise NotImplementedError

    def _triggerEvent(self, event):
        if not isinstance(event, Event):
            self.returnError(NonEventError("%r is not an Event!"%(event)))
        for e, a in self.getCurrentEvents():
            if isinstance(event, e):
                action = a
                break
        else:
            print "fell off the end"
            self.returnError(EventNotSpecifiedError(
                            "No matching event for %s in state %s"
                            %(event.getEventName(), self.getCurrentState())))
            return
        self._doState(action, event)

    def getCurrentState(self):
        return self._curState

    def getCurrentEvents(self):
        return self._curEvents

    def raiseEvent(self, evt):
        reactor.callLater(0, lambda e=evt: self._triggerEvent(evt))

    def _doState(self, callable, evt=None):
        self._curState = callable.__name__
        if evt:
            em = callable(evt)
        else:
            em = callable()
        self._curEvents = em

    def _start(self):
        self._doState(self.__start__)
        self._triggerEvent(CallStartedEvent())

