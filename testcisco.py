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

import time

class PlayingApp(VoiceApp):

    saveFile = None
    callURL = None

    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        self.leg = None
        if not self.callURL:
            raise ValueError, "must supply callURL"        
        super(PlayingApp, self).__init__(*args, **kwargs)

    def __start__(self):
        print "starting call to", self.callURL

        return ( ( CallStartedEvent, self.makeACall), )

    def makeACall(self, event):
        self.timestats = [time.time()]
        self.placeCall(self.callURL, 'sip:testcall@divmod.com')
        return ( (CallAnsweredEvent, self.callAnswered),
                 (CallRejectedEvent, self.callFailed), 
                 (Event,            self.unknownEvent), 
               )

    def unknownEvent(self, event):
        print "Got unhandled event %s"%event
        return ()

    def callAnswered(self, event):
        self.timestats.append(time.time())
        leg = event.getLeg()
        self.dtmfMode(single=True, inband=True)
        self.leg = leg
        self.leg.hijackLeg(self)
        username = leg._dialog.getCallee().getURI().username
        print "voiceapp.__start__ to user %s"%(username)
        #self.mediaPlay(self.announceFile)
        if self.saveFile is not None:
            self.mediaRecord(self.saveFile)
        self.setTimer(45)
        return ( (MediaDoneEvent, self.messageDone),
                 (DTMFReceivedEvent, self.dtmfEnterAccount),
                 (TimeoutEvent, self.doneRecording),
                 (CallEndedEvent, self.doneDoneAndDone),
               )

    def dtmfEnterAccount(self, event):
        if event.digits == '7':
            print "got login!"
            self.leg.sendDTMF('2030303030#')
        else:
            print "got unknown event", event.digits
            self.callFailed(None)
        return ( (MediaDoneEvent, self.messageDone),
                 (DTMFReceivedEvent, self.dtmfEnterPin),
                 (TimeoutEvent, self.doneRecording),
                 (CallEndedEvent, self.doneDoneAndDone),
               )

    def dtmfEnterPin(self, event):
        print "got pin!"
        if event.digits == '2':
            print "account ok!"
            self.leg.sendDTMF('3030#')
            self.timestats.append(time.time())
            return ( (MediaDoneEvent, self.messageDone),
                     (DTMFReceivedEvent, self.dtmfMainMenu),
                     (TimeoutEvent, self.doneRecording),
                     (CallEndedEvent, self.doneDoneAndDone),
                   )
        elif event.digits == '9':
            print "account nak!"
            self.callFailed(None)
        else:
            print "unknown result", event.digits
            self.callFailed(None)

    def dtmfMainMenu(self, event):
        if event.digits == '4':
            print "pin ok!"
            self.leg.sendDTMF('9')
            self.timestats.append(time.time())
            self.leg.hangupCall()
            self.doneDoneAndDone(None)
            return ( (MediaDoneEvent, self.messageDone),
                     (TimeoutEvent, self.doneRecording),
                     (CallEndedEvent, self.doneDoneAndDone),
                   )
        elif event.digits == '0':
            print "account nak!"
            self.callFailed(None)
        else:
            print "unknown result", event.digits

    def doneRecording(self, event):
        self.mediaStop()
        return self.messageDone(event)

    def messageDone(self, event):
        self.leg.hangupCall()
        return ( (CallEndedEvent, self.doneDoneAndDone),
               )

    def doneDoneAndDone(self, event):
        self.mediaStop()
        self.returnResult(self.timestats)

    def callFailed(self, event):
        if self.leg:
            self.leg.hangupCall()
        self.mediaStop()
        self.returnResult(None)

# Hack hack hack.
import sys ; sys.path.append(sys.path.pop(0))

app = None

from shtoom.app.doug import DougApplication
class MyDougApplication(DougApplication):
    def acceptResults(self, cookie, results):
        from twisted.internet import reactor
        fp = open('calltiming.out','a')
        if type(results) is list:
            s,conn,pin,loggedin = results
            fp.write('%d %s: %.2f %.2f %.2f\n'%(s, self._voiceappArgs['callURL'], (conn-s), (loggedin - pin), (loggedin - s)))
            fp.close()
        # Hack until dropCall returns a deferred.
        reactor.callLater(0.4, reactor.stop)

def main():
    from twisted.internet import reactor
    global app

    app = MyDougApplication(PlayingApp)
    app.boot()
    reactor.callLater(0,app.startVoiceApp)
    app.start()

if __name__ == "__main__":
    main()

