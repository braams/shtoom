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
from shtoom.app.doug import DougApplication
from shtoom.doug.events import *

from shtoom.exceptions import CallRejected
from twisted.python import log

def draftTemp(dest):
    import sha, os, time
    s = sha.new()
    s.update(str(os.getpid()))
    s.update(str(time.time()))
    s.update(str(dest))
    return s.hexdigest()


class VoicemailApp(VoiceApp):

    announceFile = 'voicemail.raw'
    # Maximum record time, in seconds
    maxDuration = 300
    draftDir = '/tmp'

    def __start__(self):
        print "voiceapp.__start__"
        return ( (CallStartedEvent, self.answerCall),
                 #(Event,            self.unknownEvent),
               )

    def unknownEvent(self, event):
        print "Got unhandled event %s"%event
        return ()

    def checkUser(self, username):
        "returns True/False for whether to accept voicemail for the user"
        if not '@' in username:
            return 0
        else:
            return 1

    def getUserAnnounceFile(self, username):
        "Per user announcement"
        return None

    def answerCall(self, event):
        self.leg = event.getLeg()
        dialog = self.leg.getDialog()
        destURI = dialog.getCallee().getURI(parsed=True)
        self.sender = dialog.getCaller().getURI(parsed=True)
        user, host = destURI.username, destURI.host
        if '+' in user:
            d = self.destination = user.replace('+','@')
        else:
            d = self.destination = '%s@%s'%(user, host)
        print "voiceapp.__start__ to user %s"%(d)
        if not self.checkUser(d):
            self.leg.rejectCall(CallRejected("won't accept voicemail for %s"%d))
            return
        self.leg.answerCall(self)
        return ( (CallAnsweredEvent, self.playAnnounce),
               )

    def playAnnounce(self, event):
        announce = False
        if self.announceFile:
            self.mediaPlay(self.announceFile)
            announce = True
        userann = self.getUserAnnounceFile(self.destination)
        if userann:
            self.mediaPlay(userann)
            announce = True
        if announce:
            return ( (MediaDoneEvent, self.beginRecording),
                     (CallEndedEvent,  self.allDone),
                   )
        else:
            return self.beginRecording(event=None)

    def beginRecording(self, event):
        self.draftFile = os.path.join(self.draftDir,
                                'vmdraft%s.raw'%draftTemp(self.destination))
        self.recordingTimeout = self.setTimer(self.maxDuration)
        self.mediaRecord(self.draftFile)
        return ( (CallEndedEvent, self.recordingDone),
                 (TimeoutEvent, self.recordingTooLong),
               )

    def recordingTooLong(self, event):
        # XXX tell the user they talk too much.
        self.mediaStop()
        self.leg.hangupCall()
        return self.recordingDone(event)

    def recordingDone(self, event):
        # Sweet. Recording is in self.draftFile, destination is self.destination
        self.returnResult((self.destination, self.sender, self.draftFile))

    def allDone(self, event):
        self.returnResult('other end closed without leaving a message')


def encodeAudio(infp, dest):
    import wave
    draft = os.path.join('/tmp','voicemail%s.wav'%draftTemp(dest))
    fp = wave.open(draft, 'wb')
    fp.setparams((1,2,8000,0,'NONE','NONE'))
    fp.writeframes(infp.read())
    fp.close()
    return draft

def sendVoicemail(dest, sender, draftfile):
    import smtplib
    from email.MIMEAudio import MIMEAudio
    from email.Message import Message
    infp = open(draftfile,'rb')
    draft = encodeAudio(infp, dest)
    print "wav is in", draft
    audio = MIMEAudio(open(draft).read())
    sender = '%s@%s'%(sender.username, sender.host)
    audio['Subject'] = 'A voicemail from %s'%sender
    audio['From'] = sender
    audio['To'] = dest
    server = smtplib.SMTP('localhost')
    server.set_debuglevel(0)
    server.sendmail(sender, dest, str(audio))
    server.quit()

class VoicemailApplication(DougApplication):
    configFileName = '.shtamrc'

    def acceptResults(self, cookie, result):
        from twisted.internet import reactor
        if isinstance(result, basestring):
            # A message, no returned message
            log.msg("voicemail failed to collect a message: %s"%result)
        else:
            dest, sender, draft = result
            print "message for %s from %s in %s"%(dest, sender, draft)
            reactor.callInThread(lambda : sendVoicemail(dest, sender, draft))
            log.msg("sent voicemail %r to %s"%(draft, dest))

def main():
    global app
    from twisted.internet import reactor

    app = VoicemailApplication(VoicemailApp)
    app.boot(args=sys.argv[1:])
    app.start()

if __name__ == "__main__":
    main()
