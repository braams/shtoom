#!/usr/bin/env python
# Hack hack hack.
# This thing allows the script to be run from a subdirectory of the
# source code without having to explicitly set the PYTHONPATH or
# install the shtoom code.
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


class MessageApp(VoiceApp):

    # Set the announceFile. This can also be set with the
    # option 'dougargs=announceFile=foobar.raw'. As with all
    # files in doug, this should be 8KHz 16 bit linear PCM
    # audio.
    announceFile = None
    callURL = 'sip:600@10.98.1.17'

    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        super(MessageApp, self).__init__(*args, **kwargs)

    # The __start__ method is the only *required* method for a
    # VoiceApp. It's called to boot the app. As with all VoiceApp
    # methods, it returns a list of two-tuples. The two-tuples
    # are (event, handler). Note that the events are in a hierarchy,
    # rooted at Event.
    def __start__(self):
        print "ANNOUNCING", self.announceFile
        # When a call starts, call the 'answerCall' method.
        return ( (CallStartedEvent, self.answerCall),
               )

    # The event system will call the method 'unknownEvent' if it
    # exists and there's an unhandled event.
    def unknownEvent(self, event):
        log.msg("Got unhandled event %r"%event)
        return ()

    # When a call comes in, this method will be called - we defined
    # this back in the __start__ method, above.
    def answerCall(self, event):
        # A CallStarted event has a leg associated with it - this is
        # the leg that represents the incoming call.
        self.leg = event.getLeg()
        # From the leg, we can get to the Dialog object that represents
        # the SIP Dialog. From this, we ask for the Callee (the address
        # that was called), and then the URI of the callee. Finally,
        # we ask for the username part of the sip call. If that's the
        # string 'nope', we punt the call.
        username = self.leg.getDialog().getCallee().getURI().username
        if username == 'nope':
            # To refuse to accept the call, call the leg.rejectCall method,
            # passing an exception that explains why.
            self.leg.rejectCall(CallRejected('go away'))
        else:
            # Otherwise, we accept the call.
            self.leg.answerCall(self)
        # When the call is answered, start the announcement
        return ( (CallAnsweredEvent, self.playAnnounce),
               )

    # This method is called when the leg is connected
    def playAnnounce(self, event):
        # mediaPlay queues up a source of audio to be played. In
        # the future, you'll also be able to call 'leg.mediaPlay'
        self.mediaPlay(self.announceFile)
        # more state setting. When the queue of media is finished,
        # end the call. If the other end hangs up, go to the end
        # of the app.
        return ( (MediaDoneEvent, self.startOutbound),
                 (CallEndedEvent,  self.allDone),
               )

    # Now make an outbound call, and bridge them together
    def startOutbound(self, event):
        leg = self.getDefaultLeg()
        caller = leg.getDialog().getCallee().getURI()
        self.placeCall(self.callURL, caller)
        return ( (CallAnsweredEvent, self.callAnswered),
                 (CallRejectedEvent, self.outboundEnded),
                 (CallEndedEvent, self.outboundEnded),
                 (Event,             self.unknownEvent),
               )

    def callAnswered(self, event):
        inleg = self.getDefaultLeg()
        outleg = event.getLeg()
        print "bridging legs", inleg, outleg
        b = self.connectLegs(inleg, outleg)
        print "bridged with", b

    def outboundEnded(self, event):
        print "got event", event
        self.endCall(event)

    def endCall(self, event):
        # The media is finished. Drop the call.
        self.leg.hangupCall()
        return ( (CallEndedEvent, self.allDone),
               )

    def allDone(self, event):
        # We're finished. Use the returnResult to pass the result
        # back to the DougApplication that is the parent of this
        # VoiceApp. We could also use returnError if something went
        # wrong.
        self.returnResult('other end closed')

def main():
    global app
    from twisted.internet import reactor

    app = DougApplication(MessageApp)
    app.configFileName = '.shmessagerc'

    app.boot(args=sys.argv[1:])
    app.start()

if __name__ == "__main__":
    from shtoom import i18n
    i18n.install()
    main()
