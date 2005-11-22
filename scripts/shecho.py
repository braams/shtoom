#!/usr/bin/env python

# Hack hack hack.
import sys, os
f = sys.path.pop(0)
if f.endswith('scripts') and os.path.isdir(os.path.join(os.path.dirname(f),
                                                        'shtoom')):
    sys.path.insert(0, os.path.dirname(f))
else:
    sys.path.append(f)



from shtoom.doug import VoiceApp
from shtoom.app.doug import DougApplication
from shtoom.doug.events import *

from shtoom.exceptions import CallRejected
from twisted.python import log


class EchoApp(VoiceApp):

    announceFile = None

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
        if self.announceFile:
            self.mediaPlay(self.announceFile)
            return ( (MediaDoneEvent, self.beginEcho),
                     (CallEndedEvent,  self.allDone),
                   )
        else:
            return self.beginEcho(event=None)

    def beginEcho(self, event):
        from shtoom.doug.source import EchoSource
        e = EchoSource(delay=1.0)
        self.mediaPlay([e,])
        self.mediaRecord(e)
        return ( (CallEndedEvent, self.allDone),
                   )

    def allDone(self, event):
        self.returnResult('other end closed')


class EchoApplication(DougApplication):
    configFileName = '.shechorc'

def main():
    global app
    from twisted.internet import reactor

    app = EchoApplication(EchoApp)
    app.boot(args=sys.argv[1:])
    app.start()

if __name__ == "__main__":
    main()
