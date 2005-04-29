#!/usr/bin/env python
#
# Hack hack hack.
import sys, os
f = sys.path.pop(0)
if f.endswith('scripts') and os.path.isdir(os.path.join(os.path.dirname(f),
                                                        'shtoom')):
    sys.path.insert(0, os.path.dirname(f))
else:
    sys.path.append(f)



from shtoom.doug import VoiceApp
from shtoom.doug.events import *

from shtoom.exceptions import CallRejected

class RecordingApp(VoiceApp):

    announceFile = 'tmp/doug_welcome.raw'
    testRecordingFile = 'tmp/recording.raw'

    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        if not self.announceFile:
            raise ValueError, "must supply announceFile"
        super(RecordingApp, self).__init__(*args, **kwargs)

    def __start__(self):
        print "voiceapp.__start__"
        return ( (CallStartedEvent, self.answerCall),
                 #(Event,            self.unknownEvent),
               )

    def unknownEvent(self, event):
        print "Got unhandled event %s"%event
        return ()

    def answerCall(self, event):
        leg = event.getLeg()

        username = leg.getDialog().getCallee().getURI().username
        print "voiceapp.__start__ to user %s"%(username)
        if username == 'nope':
            leg.rejectCall(CallRejected('go away'))
        else:
            leg.answerCall(self)
        return ( (CallAnsweredEvent, self.playAnnounce),
               )

    def playAnnounce(self, event):
        # Begin the call

        # We want to receive the DTMF one keystroke at a time.
        self.dtmfMode(single=True)
        self.mediaPlay(self.announceFile)
        return ( (MediaDoneEvent, self.waitForAKey),
                 (CallEndedEvent,  self.allDone),
                 (DTMFReceivedEvent,      self.gotAKey),
                 #(Event,          self.unknownEvent),
               )

    def waitForAKey(self, event):
        return ( (CallEndedEvent, self.allDone),
                 (MediaDoneEvent, IGNORE_EVENT),
                 (DTMFReceivedEvent, self.gotAKey),
                # (Event,     self.unknownEvent),
               )

    def gotAKey(self, event):
        sounds = { '1': 'one', '2':'two', '3':'three', '4':'four', '5':'five',
                   '6': 'six', '7':'seven', '8':'eight', '9':'nine', '0':'zero',
                   '*': 'star' }
        print "got digit", event.digits
        s = sounds.get(event.digits)
        if s:
            self.mediaPlay('tmp/%s.raw'%s)
            if event.digits == '2':
                from shtoom.doug.source import EchoSource
                self.mediaPlay([EchoSource(delay=1.0)])
                return ( (DTMFReceivedEvent, self.echoDone),
                         (CallEndedEvent, self.allDone),
                       )
            if event.digits == '5':
                self._recordT = self.setTimer(10.0)
                self.mediaRecord(self.testRecordingFile)
                return ( (DTMFReceivedEvent, self.recordingDone),
                         (TimeoutEvent, self.recordingDone),
                         (CallEndedEvent, self.allDone),
                       )
        elif event.digits == '#':
            self.mediaPlay('tmp/goodbye.raw')
            return ( (CallEndedEvent, self.allDone),
                     (MediaDoneEvent, self.endCall),
                     (Event,     IGNORE_EVENT),
                   )
        else:
            print "unknown key %r"%(event.digits)
        return ( (CallEndedEvent, self.allDone),
                 (MediaDoneEvent, IGNORE_EVENT),
                 (DTMFReceivedEvent, self.gotAKey),
                 (Event,     IGNORE_EVENT),
               )

    def echoDone(self, event):
        self.mediaStop()
        return self.waitForAKey(event=None)

    def recordingDone(self, event):
        if not isinstance(event, TimeoutEvent):
            self._recordT.cancel()
        self.mediaStop()
        self.mediaPlay(self.testRecordingFile)
        return ( (CallEndedEvent, self.allDone),
                 (MediaDoneEvent, self.waitForAKey),
                 (DTMFReceivedEvent, self.gotAKey),
               )

    def allDone(self, event):
        self.returnResult('other end closed')

    def endCall(self, event):
        self.returnResult('done')



from shtoom.doug.service import DougService
from shtoom.i18n import install ; install()
global app
srv = DougService(RecordingApp)
srv.startService()
app = srv.app
#app.boot()
#app.start()
