# Copyright (C) 2004 Anthony Baxter

""" VoiceApp base class

    This is just a first cut at the VoiceApp. Do NOT assume that 
    the interfaces here won't be entirely rewritten in the future.

    In fact, ASSUME that they will be rewritten entirely. Repeatedly.

"""

from shtoom.doug.events import *
from shtoom.doug.exceptions import *

from twisted.internet import reactor

class StateMachine(object):

    def __init__(self, defer, **kwargs):
        self._doneDeferred = defer

    def returnResult(self, result):
        d, self._doneDeferred = self._doneDeferred, None
        d.callback(result)

    def returnError(self, exc):
        d, self._doneDeferred = self._doneDeferred, None
        d.errback(exc)

    def __start__(self):
        raise NotImplementedError

    def _triggerEvent(self, event):
        if not isinstance(event, Event):
            self.returnError(NonEventError("%r is not an Event!"%(event)))
        for e, a in self.getCurrentEvents():
            if isinstance(event, e):
                action = a
                self._doState(action, event)
                break
        else:
            self.returnError(EventNotSpecifiedError(
                            "No matching event for %s in state %s"
                            %(event.getEventName(), self.getCurrentState())))
            return

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
        self._triggerEvent(CallStartedEvent(None))

    def __start__(self):
        raise NotImplementedError

