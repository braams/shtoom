#
# This is a test-bed for working out _how_ a VoiceApp would look.
# 
# This is _one_ way of spelling it. A more sophisticated approach
# would be to use PEAK. The PEAK docs make my brain hurt right now,
# so I'm going to come back to that later.
# 

from shtoom.doug import VoiceApp
from shtoom.doug.events import *

class RecordingApp(VoiceApp):

    announceFile = None
    menuFile = None
    draftFile = None

    def __init__(self, **kw):
        self.__dict__.update(kw)
        if not self.announceFile:
            raise ValueError, "must supply announceFile"        
        if not self.menuFile:
            raise ValueError, "must supply menuFile"        
        super(self, RecordingApp).__init__(self, **kwargs)

    def __start__(self):
        return ( (CallStartedEvent, self.playAnnounce),
                 (Event,            self.unknownEvent), )

    def unknownEvent(self, event):
        print "Got unhandled event %s"%event

    def playAnnounce(self, event):
        # Begin the call

        # We want to receive the DTMF one keystroke at a time.
        self.dtmfMode(single=True)
        self.mediaPlay(self.announceFile)
        return ( (MediaDoneEvent, self.recordDraft), 
                 (CallDoneEvent,  self.discardDone),
                 (DTMFEvent,      self.recordDraft),
                 (Event,          self.unknownEvent), )

    def recordDraft(self, event):
        if self.isPlaying():
            self.mediaStop()
        self.draftFile = self.getTempFile()
        self.mediaRecord(self.draftFile)
        return ( (CallDoneEvent, self.saveDone),
                 (DTMFEvent, self.playDraftMenu),
                 (Event,     self.unknownEvent), )

    def playDraft(self, event):
        self.mediaPlay(self.draftFile)
        return ( (MediaDoneEvent, self.playDraftMenu),
                 (CallDoneEvent,  self.saveDone),
                 (DTMFEvent,      self.processDraftMenu), 
                 (Event,          self.unknownEvent), )

    def playDraftMenu(self, event):
        self.mediaPlay(self.menuFile)
        return ( (DTMFEvent,      self.processDraftMenu),
                 (CallDoneEvent,  self.saveDone),
                 (Event,          self.unknownEvent), )

    def processDraftMenu(self, event):
        if self.isRecording():
            self.mediaStop()
        if event.digits:
            if event.digits == '1':
                self.saveDone(event)
            elif event.digits == '2':
                self.playDraft(event)
            elif event.digits == '3':
                self.playAnnounce(event)
            elif event.digits == '4':
                self.discardDone(event)
        else:
            # timeout
            self.playDraftMenu(event)

    def saveDone(self, event):
        self.returnResult(self.draftFile)

    def discardDone(self, event):
        self.cleanUp()
        self.returnResult(None)

