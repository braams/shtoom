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
from shtoom.i18n import install as i18n_install
i18n_install()

from twisted.python import log

log.FileLogObserver.timeFormat = "%Y/%m/%d %H:%M:%S"

import time

class PlayingApp(VoiceApp):

    saveFile = None
    callURL = None
    account = '2030303030'
    pin = '3030'

    def __init__(self, *args, **kwargs):
        self.where = 'init'
        self.__dict__.update(kwargs)
        self.leg = None
        if not self.callURL:
            raise ValueError, "must supply callURL"
        super(PlayingApp, self).__init__(*args, **kwargs)

    def __start__(self):
        self.where = 'start'
        print "starting call to", self.callURL
        self.setTimer(45)
        return ( ( CallStartedEvent, self.makeACall), )

    def makeACall(self, event):
        self.where = 'placeCall'
        self.timestats = [time.time()]
        self.placeCall(self.callURL, 'sip:testcall@ekit-inc.com')
        return ( (CallAnsweredEvent, self.callAnswered),
                 (CallRejectedEvent, self.callFailed),
                 (CallEndedEvent, self.callFailed),
                 (TimeoutEvent,      self.callTimedOut),
                 (Event,             self.unknownEvent),
               )

    def unknownEvent(self, event):
        self.where = 'unknown'
        print "Got unhandled event %s"%event
        return self.callFailed(event)

    def callAnswered(self, event):
        self.where = 'answered'
        self.timestats.append(time.time())
        leg = event.getLeg()
        self.dtmfMode(single=True, inband=True)
        self.leg = leg
        self.leg.hijackLeg(self)
        username = leg.getDialog().getCallee().getURI().username
        print "voiceapp.__start__ to user %s"%(username)
        if self.saveFile is not None:
            self.leg.mediaRecord(self.saveFile)
        return ( (MediaDoneEvent, self.messageDone),
                 (DTMFReceivedEvent, self.dtmfEnterAccount),
                 (TimeoutEvent, self.callTimedOut),
                 (CallEndedEvent, self.callFailed),
               )

    def dtmfEnterAccount(self, event):
        self.where = 'enter account'
        if event.digits == '7':
            print "got login!"
            self.leg.sendDTMF(self.account+'#')
            self.timestats.append(time.time())
        else:
            print "got unknown event", event.digits
            self.callFailed(event)
        return ( (MediaDoneEvent, self.messageDone),
                 (DTMFReceivedEvent, self.dtmfEnterPin),
                 (TimeoutEvent, self.callTimedOut),
                 (CallEndedEvent, self.callFailed),
               )

    def dtmfEnterPin(self, event):
        self.where = 'enter pin'
        print "got pin!"
        if event.digits == '2':
            print "account ok!"
            self.leg.sendDTMF(self.pin+'#')
            self.timestats.append(time.time())
            return ( (MediaDoneEvent, self.messageDone),
                     (DTMFReceivedEvent, self.dtmfMainMenu),
                     (TimeoutEvent, self.callTimedOut),
                     (CallEndedEvent, self.callFailed),
                   )
        elif event.digits == '9':
            print "account nak!"
            self.callFailed(event)
        else:
            print "unknown result", event.digits
            self.callFailed(event)

    def dtmfMainMenu(self, event):
        self.where = 'main menu'
        if event.digits == '4':
            print "pin ok!"
            self.leg.sendDTMF('9')
            self.timestats.append(time.time())
            self.leg.hangupCall()
            self.doneDoneAndDone(None)
            return ( (MediaDoneEvent, self.messageDone),
                     (TimeoutEvent, self.callTimedOut),
                     (CallEndedEvent, self.doneDoneAndDone),
                   )
            #print "dialling"
            #self.leg.sendDTMF('2,,,,12138672411#')
            #return ( (MediaDoneEvent, self.messageDone),
            #         (DTMFReceivedEvent, self.dtmfVoicemailLogin),
            #         (TimeoutEvent, self.callTimedOut),
            #         (CallEndedEvent, self.callFailed),
            #       )
        elif event.digits == '0':
            print "account nak!"
            self.callFailed(event)
        else:
            print "unknown result", event.digits

    def dtmfVoicemailLogin(self, event):
        self.where = 'voicemail'
        print "voicemail login", event.digits
        self.leg.hangupCall()
        self.doneDoneAndDone(None)
        return ( (CallEndedEvent, self.callFailed), )

    def callTimedOut(self, event):
        return self.callFailed(event, 'timeout')

    def messageDone(self, event):
        self.leg.hangupCall()
        return ( (CallEndedEvent, self.doneDoneAndDone),
               )

    def doneDoneAndDone(self, event):
        self.leg.mediaStop()
        self.returnResult(self.timestats)

    def callFailed(self, event, optional=''):
        if self.leg:
            self.leg.hangupCall()
            self.leg.mediaStop()
        self.returnError('%s (in %s) %s'%(event, self.where, optional))

# Hack hack hack.
import sys ; sys.path.append(sys.path.pop(0))

app = None

from shtoom.app.doug import DougApplication

def ts():
    return time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime())

class MyDougApplication(DougApplication):

    def acceptErrors(self, cookie, error):
        from twisted.internet import reactor
        actualError = error.value
        fp = open('calltiming.out','a')
        fp.write('%s %s: FAILED %s\n'%(ts(),  self._voiceappArgs['callURL'], actualError))
        fp.close()
        # Hack until dropCall returns a deferred.
        reactor.callLater(0.4, reactor.stop)

    def acceptResults(self, cookie, results):
        from twisted.internet import reactor
        fp = open('calltiming.out','a')
        if type(results) is list and len(results) == 5:
            s,conn,ac,pin,loggedin = results
            pintime = len(self._voiceappArgs['pin'])*0.15 + 0.10
            actime = len(self._voiceappArgs['account'])*0.15 + 0.10
            fp.write('%s %s: connect:%.2f accheck:%.2f pincheck:%.2f total:%.2f\n'%(ts(), self._voiceappArgs['callURL'], (conn-s), (pin-ac)-actime, (loggedin - pin)-pintime, (loggedin - s)))
            fp.close()
        else:
            fp.write('%s %s: FAILED\n'%(ts(), self._voiceappArgs['callURL']))
            log.msg("err, got results %r"%(results))
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
