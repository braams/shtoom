#
# This is a test-bed for working out _how_ a VoiceApp would look.
# 
# This is _one_ way of spelling it. A more sophisticated approach
# would be to use PEAK. The PEAK docs make my brain hurt right now,
# so I'm going to come back to that later.
# 

from shtoom.doug import VoiceApp
from shtoom.doug.events import *

from shtoom.exceptions import CallRejected

class ConferencingApp(VoiceApp):

    announceFile = 'tmp/doug_welcome.raw'
    conf = None

    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        if not self.announceFile:
            raise ValueError, "must supply announceFile"        
        super(ConferencingApp, self).__init__(*args, **kwargs)

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

        username = leg._dialog.getCallee().getURI().username
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
        return ( (MediaDoneEvent, self.startConference), 
                 (CallEndedEvent,  self.allDone),
                 (DTMFReceivedEvent,      self.startConference),
                 #(Event,          self.unknownEvent), 
               )

    def startConference(self, event):
        from shtoom.doug.conferencing import newConferenceMember
        self.mediaStop()
        self.conf = newConferenceMember('101')
        self.mediaPlay([self.conf])
        return ( (MediaDoneEvent, self.startConference), 
                 (CallEndedEvent,  self.allDone),
                 (DTMFReceivedEvent,      IGNORE_EVENT),
                 #(Event,          self.unknownEvent), 
               )


    def allDone(self, event):
        self.conf.close()
        self.mediaStop()
        self.returnResult('other end closed')


# Hack hack hack.
import sys ; sys.path.append(sys.path.pop(0))


from shtoom.doug.service import DougService
global app
srv = DougService(ConferencingApp)
srv.startService()
app = srv.app
#app.boot()
#app.start()


