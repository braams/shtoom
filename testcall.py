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

class PlayingApp(VoiceApp):

    announceFile = 'tmp/doug_welcome.raw'
    callURL = 'sip:anthony@localhost:5061'

    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        if not self.announceFile:
            raise ValueError, "must supply announceFile"        
        super(PlayingApp, self).__init__(*args, **kwargs)

    def __start__(self):
        print "starting"

        return ( ( CallStartedEvent, self.makeACall), )

    def makeACall(self, event):
        self.placeCall(self.callURL)
        return ( (CallAnsweredEvent, self.callAnswered),
                 (CallRejectedEvent, self.callFailed), 
                 (Event,            self.unknownEvent), 
               )

    def unknownEvent(self, event):
        print "Got unhandled event %s"%event
        return ()

    def callAnswered(self, event):
        leg = event.getLeg()

        username = leg._dialog.getCallee().getURI().username
        print "voiceapp.__start__ to user %s"%(username)
        self.connectLeg(leg)
        self.mediaPlay(self.announceFile)
        return ( (MediaDoneEvent, self.messageDone),
               )

    def messageDone(self, event):
        self.returnResult('done')

    def callFailed(self, event):
        self.returnResult('failed')

# Hack hack hack.
import sys ; sys.path.append(sys.path.pop(0))

app = None

def main():
    from shtoom.app.doug import DougApplication
    from twisted.internet import reactor
    global app

    app = DougApplication(PlayingApp)
    app.boot()
    reactor.callLater(0,app.startVoiceApp)
    app.start()

if __name__ == "__main__":
    main()

