# Copyright (C) 2004 Anthony Baxter

""" VoiceApp base class

    This is just a first cut at the VoiceApp. Do NOT assume that
    the interfaces here won't be entirely rewritten in the future.

    In fact, ASSUME that they will be rewritten entirely. Repeatedly.

"""

from shtoom.doug.events import *
from shtoom.doug.exceptions import *

from twisted.internet import reactor
from twisted.python import log

class StateMachine(object):

    def __init__(self, defer, **kwargs):
        self._doneDeferred = defer

    def returnResult(self, result):
        d, self._doneDeferred = self._doneDeferred, None
        if d:
            d.callback(result)

    def returnError(self, exc):
        d, self._doneDeferred = self._doneDeferred, None
        if d:
            d.errback(exc)

    def __start__(self):
        raise NotImplementedError

    def _triggerEvent(self, event):
        if self._doneDeferred is None:
            # We're already done
            return
        if not isinstance(event, Event):
            self.returnError(NonEventError("%r is not an Event!"%(event)))
        for e, a in self.getCurrentEvents():
            if isinstance(event, e):
                action = a
                if action == IGNORE_EVENT:
                    return
                self._doState(action, event)
                break
        else:
            log.msg("No matching event for %s in state %s"%(
                            event.getEventName(), self.getCurrentState()))
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
        if self._doneDeferred is None:
            # We're done.
            self._curEvents = ()
            self._curState = '<done>'
        else:
            try:
                i = iter(em)
            except TypeError:
                print "%s did not return a new state mapping, but %r"%(
                                                self._curState, em)
                em = self._curEvents
        self._curEvents = em

    def _start(self, callstart=1):
        self._doState(self.__start__)
        if callstart:
            self._triggerEvent(CallStartedEvent(None))

    def __start__(self):
        raise NotImplementedError
