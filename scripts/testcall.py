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
        self.placeCall(self.callURL, 'sip:testcall@divmod.com')
        return ( (CallAnsweredEvent, self.callAnswered),
                 (CallRejectedEvent, self.callFailed),
                 (Event,            self.unknownEvent),
               )

    def unknownEvent(self, event):
        print "Got unhandled event %s"%event
        return ()

    def callAnswered(self, event):
        leg = event.getLeg()

        self.leg = leg
        self.leg.hijackLeg(self)
        username = leg.getDialog().getCallee().getURI().username
        print "voiceapp.__start__ to user %s"%(username)
        self.mediaPlay(self.announceFile)
        return ( (MediaDoneEvent, self.messageDone),
               )

    def messageDone(self, event):
        self.leg.hangupCall()
        return ( (CallEndedEvent, self.doneDoneAndDone),
               )

    def doneDoneAndDone(self, event):
        self.returnResult('done')

    def callFailed(self, event):
        self.returnResult('failed')

app = None

from shtoom.app.doug import DougApplication
class MyDougApplication(DougApplication):
    def acceptResults(self, cookie, results):
        from twisted.internet import reactor
        self.dropCall(cookie)
        # Hack until dropCall returns a deferred.
        reactor.callLater(0.4, reactor.stop)

def main():
    from twisted.internet import reactor
    global app

    app = MyDougApplication(PlayingApp)
    app.boot(args=sys.argv[1:])
    reactor.callLater(0,app.startVoiceApp)
    app.start()

if __name__ == "__main__":
    main()
