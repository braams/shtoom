# Copyright (C) 2004 Anthony Baxter


class Event(object):
    """
    """
    def getEventName(self):
        return self.__class__.__name__

    def _extraRepr(self):
        return ''

    def __repr__(self):
        e = self._extraRepr()
        if e: e = '(%s) '%e
        return '<%s %sat %x>'%(self.__class__.__name__, e, id(self))

class    DTMFReceivedEvent(Event):
    """ Received some DTMF keystrokes.
    """
    def __init__(self, digits, leg):
        self.digits = digits
        self.leg = leg

    def _extraRepr(self):
        return str(self.digits)

class        DTMFTimeoutEvent(DTMFReceivedEvent):
    """ A timeout occurred while collecting DTMF.

        Any digits collected will be returned in this object's digits
        attribute.
    """

class    MediaDoneEvent(Event):
    """ A media play/record completed
    """
    def __init__(self, source, leg):
        self.source = source
        self.leg = leg

    def _extraRepr(self):
        return repr(self.source)

class        MediaPlayDoneEvent(MediaDoneEvent):
    """ A mediaPlay completed
    """

class            MediaPlayContentDoneEvent(MediaPlayDoneEvent):
    """ A mediaPlay completed because it finished with the content
    """

class            MediaPlayContentFailedEvent(MediaPlayDoneEvent):
    """ A mediaPlay completed because the source of audio failed
    """

class            MediaPlayUserBargeInEvent(DTMFReceivedEvent,
                                           MediaPlayDoneEvent):
    """ A mediaPlay completed because the user hit a key
    """

class            MediaPlayTimerExpiredEvent(MediaPlayDoneEvent):
    """ A mediaPlay completed because a timeout was exceeded
    """

class            MediaPlayRemoteClosedEvent(MediaPlayDoneEvent):
    """
    """


class        MediaRecordDoneEvent(MediaDoneEvent):
    """ media record done
    """

class            MediaRecordRemoteClosedEvent(MediaRecordDoneEvent):
    """ A media record ended because the remote end closed the call
    """

class            MediaRecordTimeoutExceededEvent(MediaRecordDoneEvent):
    """ A media record ended because a specified timeout was exceeded
    """

class            MediaRecordFailedEvent(MediaRecordDoneEvent):
    """ A media record failed
    """

class                MediaRecordStoreFailedEvent(MediaRecordDoneEvent):
    """ A media record failed because the storage didn't work
    """

class    CallLegEvent(Event):
    """ A call event associated with a Leg
    """
    def __init__(self, leg):
        self.leg = leg

    def getLeg(self):
        return self.leg

    def _extraRepr(self):
        return repr(self.leg)


class      CallAnsweredEvent(CallLegEvent):
    """ A call was connected
    """

class      CallRejectedEvent(CallLegEvent):
    """ A call was rejected
    """
    def __init__(self, reason=''):
        self.reason = reason

    def _extraRepr(self):
        return repr(self.reason)

class      CallStartedEvent(CallLegEvent):
    """ A call started
    """
    args = None

class        InboundCallStartedEvent(CallStartedEvent):
    """ A new inbound call started
    """

class        OutboundCallStartedEvent(CallStartedEvent):
    """ A new outbound call started
    """

class    CallEndedEvent(CallLegEvent):
    """ A call under the control of this VoiceApp ended.
    """

class    TimeoutEvent(Event):
    """ A user-specified timeout occurred.

        The value of this exception is the timer that expired.
    """
    def __init__(self, timer):
        self.timer = timer

    def getTimer(self):
        return self.timer

    def _extraRepr(self):
        return repr(self.timer)

class    ApplicationSpecificEvent(Event):
    """ An Application-Specific Event.
        Subclass this to implement your own events
    """

class _IgnoranceIsBliss(Event):
    pass

IGNORE_EVENT = _IgnoranceIsBliss()

del _IgnoranceIsBliss
