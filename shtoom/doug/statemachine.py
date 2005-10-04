# Copyright (C) 2004 Anthony Baxter

""" VoiceApp base class

    This is just a first cut at the VoiceApp. Do NOT assume that
    the interfaces here won't be entirely rewritten in the future.

    In fact, ASSUME that they will be rewritten entirely. Repeatedly.

"""

from shtoom.doug.events import Event, IGNORE_EVENT, CallStartedEvent
from shtoom.doug.exceptions import NonEventError, EventNotSpecifiedError

from twisted.internet import reactor, defer
from twisted.python import log

class StateMachine(object):

    _statemachine_debug = False

    def __init__(self, defer, **kwargs):
        self._doneDeferred = defer
        self._deferredState = None

    def returnResult(self, result):
        self._cleanup()
        d, self._doneDeferred = self._doneDeferred, None
        if d:
            d.callback(result)

    def returnError(self, exc):
        self._cleanup()
        d, self._doneDeferred = self._doneDeferred, None
        if d:
            d.errback(exc)

    def _triggerEvent(self, event):
        if self._doneDeferred is None:
            # We're already done
            return
        if not isinstance(event, Event):
            self.returnError(NonEventError("%r is not an Event!"%(event)))
        if self._deferredState is not None:
            # We're waiting for a deferred to trigger to set up the state -
            # queue the event.
            self._deferredState.addCallback(lambda x, e=event:
                                            self._triggerEvent(e))
            return
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
            if self._statemachine_debug:
                log.msg("current transitions: %r"%(self.getCurrentEvents()))
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
        if self._statemachine_debug:
            if evt is not None:
                log.msg("%s switching to state %s (no event)"%(
                                self.__class__.__name__, self._curState))
            else:
                log.msg("%s switching to state %s (%s)"%(
                                self.__class__.__name__, self._curState,
                                evt.__class__.__name__))
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
                if isinstance(em, defer.Deferred):
                    self._deferredState = em
                    return em.addCallback(self._cb_doState)
                print "%s did not return a new state mapping, but %r"%(
                                                self._curState, em)
                em = self._curEvents
        self._curEvents = em

    def _cb_doState(self, result):
        self._deferredState = None
        self._curEvents = result

    def _start(self, callstart=True, args=None):
        if args is None:
            args = {}
        self._doState(self.__start__)
        if callstart:
            evt = CallStartedEvent(None)
            evt.args = args
            self._triggerEvent(evt)

    def __start__(self):
        raise NotImplementedError

    def _cleanup(self):
        # Override in subclass if needed
        pass
