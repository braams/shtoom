#!/usr/bin/env python

# Hack hack hack.
import sys, os
f = sys.path.pop(0)
if f.endswith('scripts') and os.path.isdir(os.path.join(os.path.dirname(f),
                                                        'shtoom')):
    sys.path.insert(0, os.path.dirname(f))
else:
    sys.path.append(f)

ROOMNAME="specialmagic"


from shtoom.doug import VoiceApp
from shtoom.doug.events import *

from shtoom.exceptions import CallRejected

from twisted.python import log
log.FileLogObserver.timeFormat = "%Y/%m/%d %H:%M:%S"

from twisted.web import xmlrpc, server

class ConferencingApp(VoiceApp):

    announceFile = 'tmp/conf_welcome.raw'
    leg = None

    def __init__(self, *args, **kwargs):
        self.conf = None
        self.__dict__.update(kwargs)
        if not self.announceFile:
            raise ValueError, "must supply announceFile"
        super(ConferencingApp, self).__init__(*args, **kwargs)

    def __start__(self):
        print "voiceapp.__start__"
        return ( (CallStartedEvent, self.voiceappStarted),
                 #(Event,            self.unknownEvent),
               )

    def unknownEvent(self, event):
        print "Got unhandled event %s"%event
        return ()

    def voiceappStarted(self, event):
        if event.args and 'callurl' in event.args:
            return self.makeACall(event)
        else:
            return self.answerCall(event)

    def answerCall(self, event):
        self.leg = event.getLeg()
        self.roomname = roomname = ROOMNAME

        print "voiceapp.__start__ to user %s"%(roomname)
        if roomname == 'nope':
            self.leg.rejectCall(CallRejected('go away'))
            del self.leg
        else:
            self.leg.answerCall(self)
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
        self.conf = newConferenceMember(self.roomname, self.leg)
        self.mediaPlay([self.conf])
        self.mediaRecord(self.conf)
        return ( (MediaDoneEvent, self.startConference),
                 (CallEndedEvent,  self.allDone),
                 (DTMFReceivedEvent,      IGNORE_EVENT),
                 #(Event,          self.unknownEvent),
               )


    def allDone(self, event):
        self.mediaStop()
        self.mediaStopRecording()
        del self.leg, self.conf
        self.mediaStop()
        self.returnResult('other end closed')

    def makeACall(self, event):
        url = event.args['callurl']
        self.placeCall(url, 'sip:conference@ekit-inc.com')
        return ( (CallAnsweredEvent, self.callAnswered),
                 (CallRejectedEvent, self.callFailed),
                 (CallEndedEvent, self.callFailed),
                 (Event,             self.unknownEvent),
               )

    def callAnswered(self, event):
        leg = event.getLeg()
        self.dtmfMode(single=True, inband=False)
        self.leg = leg
        self.leg.hijackLeg(self)
        self.roomname = roomname = ROOMNAME
        username = leg.getDialog().getCallee().getURI().username
        return self.startOutConference(event=None)

    def startOutConference(self, event):
        from shtoom.doug.conferencing import newConferenceMember
        self.mediaStop()
        self.conf = newConferenceMember(self.roomname, self.leg)
        self.mediaPlay([self.conf])
        self.mediaRecord(self.conf)
        return ( (MediaDoneEvent, self.startOutConference),
                 (CallEndedEvent,  self.allDone),
                 (DTMFReceivedEvent,      IGNORE_EVENT),
                 #(Event,          self.unknownEvent),
               )


    def callFailed(self, event, optional=''):
        if self.leg:
            self.leg.hangupCall()
            self.leg.mediaStop()
        self.returnError('%s %s'%(event, optional))


def makeAnOutboundCall(url):
    srv.app.startVoiceApp(callurl=url)


class ConfXMLRPC(xmlrpc.XMLRPC):
    "Management interface for XMLRPC"
    def xmlrpc_call(self, url):
        makeAnOutboundCall(url)
        return "Called %s"%url
    def xmlrpc_ping(self, x):
        return "OK"


def startXMLRPC():
    from twisted.internet import reactor
    c = ConfXMLRPC()
    reactor.listenTCP(7009, server.Site(c))

if __name__ == "__main__":
    from shtoom import i18n
    i18n.install()
    from twisted.internet import reactor
    reactor.callLater(0, startXMLRPC)
    from shtoom.doug.service import DougService
    srv = DougService(ConferencingApp)
    srv.startService(mainhack=True)

