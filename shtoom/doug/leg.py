# Copyright (C) 2004 Anthony Baxter

"""
    A Leg is a SIP connection from one UA to another UA. A typical
    voiceapp might have only one Leg (for the incoming SIP call),
    it might have two (an incoming and an outgoing leg that are
    connected, or 'conferenced' together, for instance) or indeed
    many legs (for some more exotic use-case).
"""

from shtoom.doug.source import Source, SilenceSource, convertToSource
from shtoom.audio.converters import DougConverter
from shtoom.doug.events import CallAnsweredEvent, CallRejectedEvent
from shtoom.doug.events import MediaPlayContentDoneEvent, DTMFReceivedEvent
from twisted.python import log
from twisted.internet.task import LoopingCall

class Leg(object):

    _dialog = None
    _cookie = None
    _acceptDeferred = None
    _voiceapp = None

    def __init__(self, cookie, dialog, voiceapp=None):
        """ Create a new leg
        """
        self._cookie = cookie
        self._dialog = dialog
        self._acceptDeferred = None
        self.__converter = DougConverter()
        self.__playoutList = []
        self.__silenceSource = SilenceSource()
        self.__connected = None
        self.__sink = None
        self.__currentDTMFKey = None
        self.__collectedDTMFKeys = ''
        self.__dtmfSingleMode = True
        self.__inbandDTMFdetector = None
        self._voiceapp = voiceapp
        self._connectSource(self.__silenceSource)
        self._startAudio()

    def _startAudio(self):
        #print self, "starting audio"
        self.LC = LoopingCall(self._get_some_audio)
        self.LC.start(0.020)

    def _stopAudio(self):
        if self.LC is not None:
            #print self, "stopping audio", self.LC, self.LC.call
            self.LC.stop()
            self.LC = None

    def _get_some_audio(self):
        if self._voiceapp is not None:
            data = self.__connected.read()
            sample = self.__converter.convertOutbound(data)
            self._voiceapp.va_outgoingRTP(sample, self._cookie)

    def getDialog(self):
        return self._dialog

    def getCookie(self):
        return self._cookie

    def setDialog(self, dialog):
        self._dialog = dialog

    def setCookie(self, cookie):
        self._cookie = cookie

    def incomingCall(self, d):
        " This leg is an incoming call "
        self._acceptDeferred = d

    def outgoingCall(self):
        " This leg is an outgoing call "
        pass

    def getVoiceApp(self):
        "Get the VoiceApp currently connected to this leg"
        return self._voiceapp

    def hijackLeg(self, voiceapp):
        """ Remove the currently running VoiceApp from the leg, and
            slot in a new one. Returns the hijacked app.
        """
        old, self._voiceapp = self._voiceapp, voiceapp
        return old

    def callAnswered(self, voiceapp):
        "Called when an outbound call is answered"
        self._voiceapp = voiceapp
        voiceapp._triggerEvent(CallAnsweredEvent(self))

    def callRejected(self, voiceapp):
        "Called when an outbound call is rejected"
        self._voiceapp = voiceapp
        voiceapp._triggerEvent(CallRejectedEvent(self))

    def answerCall(self, voiceapp):
        " Answer the (incoming) call on this leg "
        if self._acceptDeferred is not None:
            log.msg("%r answering this call"%(self,), system="doug")
            self._voiceapp = voiceapp
            d, self._acceptDeferred = self._acceptDeferred, None
            d.callback(self._cookie)
        else:
            log.msg("can't answer call %s, already answered/rejected"%(
                                                self._cookie), system='doug')

    def rejectCall(self, reason):
        " Reject the (incoming) call on this leg "
        if self._acceptDeferred is not None:
            d, self._acceptDeferred = self._acceptDeferred, None
            self._voiceapp = None
            self._cookie = None
            d.errback(reason)
        else:
            log.msg("can't reject call %s, already answered/rejected"%(
                                                self._cookie), system='doug')

    def hangupCall(self):
        self._stopAudio()
        if self._voiceapp:
            self._voiceapp.va_hangupCall(self._cookie)

    def sendDTMF(self, digits, duration=0.1, delay=0.05):
        self._voiceapp.sendDTMF(digits, cookie=self._cookie,
                                duration=duration, delay=delay)

    def _playNextItem(self):
        if not self.__playoutList:
            last = self._connectSource(self.__silenceSource)
            self._voiceapp._triggerEvent(MediaPlayContentDoneEvent(last, self))
        else:
            next = self.__playoutList.pop(0)
            next = convertToSource(next, 'r')
            self._connectSource(next)

    def _sourceDone(self, source):
        if self.__connected is source:
            self._playNextItem()

    def _connectSource(self, target):
        target.leg = self
        old, self.__connected = self.__connected, target
        if old:
            old.leg = None
        return old

    def _connectSink(self, target):
        if target:
            target.leg = self
        old, self.__sink = self.__sink, target
        if old:
            old.leg = None
        return old

    def _maybeStartPlaying(self):
        "Check if we're currently playing silence, and switch out if so"
        if self.__connected is self.__silenceSource:
            self._playNextItem()

    def mediaPlay(self, playlist):
        if isinstance(playlist, basestring):
            playlist = [playlist]
        self.__playoutList.extend(playlist)
        self._maybeStartPlaying()

    def mediaRecord(self, dest):
        dest = convertToSource(dest, 'w')
        self._connectSink(dest)

    def mediaStop(self):
        old = self._connectSource(self.__silenceSource)
        if old.isPlaying():
            old.close()
            self.__playoutList = []

    def mediaStopRecording(self):
        old = self._connectSink(None)
        if old and old.isRecording():
            old.close()

    def leg_startDTMFevent(self, dtmf):
        c = self.__currentDTMFKey
        if dtmf:
            if c is not dtmf:
                self.leg_stopDTMFevent(c)
                self.__currentDTMFKey = dtmf
                self._inboundDTMFKeyPress(dtmf)
            else:
                # repeat
                pass

    def _inboundDTMFKeyPress(self, dtmf):
        if self.__dtmfSingleMode:
            self._voiceapp._triggerEvent(DTMFReceivedEvent(dtmf, self))
        else:
            self.__collectedDTMFKeys += dtmf
            if dtmf in ('#', '*'):
                dtmf, self.__collectedDTMFKeys = self.__collectedDTMFKeys, ''
                self._voiceapp._triggerEvent(DTMFReceivedEvent(dtmf, self))

    def selectDefaultFormat(self, ptlist):
        return self.__converter.selectDefaultFormat(ptlist)

    def leg_stopDTMFevent(self, dtmf):
        # For now, I only care about dtmf start events
        if dtmf == self.__currentDTMFKey:
            self.__currentDTMFKey = None

    def set_handler(self, handler):
        self.__converter.set_handler(handler)

    def leg_incomingRTP(self, packet):
        data = self.__converter.convertInbound(packet)
        if self.__inbandDTMFdetector is not None:
            self.__inbandDTMFdetector(data)
        if self.__sink:
            self.__sink.write(data)

    def isPlaying(self):
        return self.__connected.isPlaying()

    def isRecording(self):
        return self.__sink and self.__sink.isRecording()

    def dtmfMode(self, single=False, inband=False, timeout=0):
        self.__dtmfSingleMode = single
        if inband:
            if numarray is None:
                raise RuntimeError, "need numarray to do inband DTMF"
            else:
                self.__inbandDTMFdetector = InbandDtmfDetector(self)
        else:
            self.__inbandDTMFdetector = None
        # XXX handle timeout

    def __repr__(self):
        return '<Leg at %x connected to %r>'%(id(self), self._voiceapp)


class BridgeSource(Source):
    "A BridgeSource connects a leg to another leg via a bridge"

    # We want DTMF
    wantsDTMF = True

    def __init__(self, bridge):
        self.bridge = bridge
        self._readbuffer = ''
        super(BridgeSource, self).__init__()

    def connect(self, other):
        self.other = other

    def isPlaying(self):
        return True

    def isRecording(self):
        return True

    def copyData(self, bytes):
        "Copy data to the other leg"
        self._readbuffer = bytes

    def read(self):
        b, self._readbuffer = self._readbuffer, ''
        return b

    def write(self, bytes):
        if self.other is not None:
            self.other.copyData(bytes)

    def close(self):
        if self.bridge is not None:
            self.leg._sourceDone(self)
            self.bridge.closeBridge(self)
            self.bridge = None
            self.other.close()
            self.other = None

class Bridge:
    """A bridge connects two legs together, and passes audio from one to
       the other. It creates two Source objects, that are connected to
       each leg"""
    def __init__(self, leg1, leg2):
        self.connectLegs(leg1, leg2)

    def connectLegs(self, l1, l2):
        bs1 = BridgeSource(self)
        bs2 = BridgeSource(self)
        bs1.connect(bs2)
        bs2.connect(bs1)
        l1._connectSource(bs1)
        l2._connectSource(bs2)

    def closeBridge(self, bs):
        # Nothing for now.
        pass



try:
    import numarray
except ImportError:
    numarray = None

if numarray is not None:
    class InbandDtmfDetector:
        def __init__(self, leg):
            from shtoom.doug.dtmf import DtmfDetector
            self.leg = leg
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
                    self.leg.leg_startDTMFevent(nd)
                elif nd == '':
                    old, self.digit = self.digit, nd
                    self.leg.leg_stopDTMFevent(old)
                else:
                    old, self.digit = nd, self.digit
                    self.leg.leg_stopDTMFevent(old)
                    self.leg.leg_startDTMFevent(self.digit)
            self.prev = samp
