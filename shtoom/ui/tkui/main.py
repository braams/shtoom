
from Tkinter import *
from twisted.python import log

from shtoom.ui.base import ShtoomBaseUI

class ShtoomMainWindow(ShtoomBaseUI):
    def __init__(self):
        self.connected = False

        self.main = Tk(className='shtoom')
        # also do hangup, shutdown reactor, &c
        self.main.protocol("WM_DELETE_WINDOW", self.shutdown)
        self._top1 = Frame(self.main)
        self._top1.pack(side=TOP, fill=X)
        self._label1 = Label(self._top1, text='SIP:')
        self._label1.pack(side=LEFT)
        self._urlentry = Entry(self._top1, width=60)
        self._urlentry.pack(side=LEFT)
        self._urlentry.bind('<Return>', self.callButton_clicked)
        self._urlentry.focus_set()
        self._top2 = Frame(self.main)
        self._top2.pack(side=TOP, fill=X)
        self._callButton = Button(self._top2, text="Call", 
                                  command=self.callButton_clicked)
        self._callButton.pack(side=LEFT)
        self._hangupButton = Button(self._top2, text="Hang up", 
                                    command=self.hangupButton_clicked,
                                    state=DISABLED)
        self._hangupButton.pack(side=LEFT)

    def getMain(self):
        return self.main

    def debugMessage(self, msg):
        print msg

    def statusMessage(self, msg):
        print "status", msg

    def errorMessage(self, message, exc=None):
        log.msg("error %s"%(message))

    def callButton_clicked(self, evt=None):
        sipURL = self._urlentry.get()
        if not sipURL.startswith('sip:'):
            log.msg("Invalid SIP url %s"%(sipURL))
            return
        self._callButton.config(state=DISABLED)
        self.connected, deferred = self.sip.placeCall(sipURL)
        deferred.addCallbacks(self.callConnected, self.callDisconnected)

    def callConnected(self, call):
        self._hangupButton.config(state=NORMAL)

    def callDisconnected(self, call):
        self.errorMessage("call failed", call)
        self._hangupButton.config(state=DISABLED)
        self._callButton.config(state=NORMAL)

    def hangupButton_clicked(self):
        self.sip.dropCall(self.connected)
        self._callButton.config(state=NORMAL)
        self._hangupButton.config(state=DISABLED)
        self.connected = False

    def shutdown(self):
        # XXX Hang up any calls
        from twisted.internet import reactor
        reactor.stop()
        self.main.quit()


    def incomingCall(self, description, call, defresp, defsetup):
        import tkMessageBox
        answer = tkMessageBox.askyesno("Shtoom", "Incoming Call: %s\nAnswer?"%description)
        print "GOT ANSWER", answer
        if answer:
            self.connected = call
            self._callButton.config(state=DISABLED)
            defsetup.addCallbacks(self.callConnected, self.callDisconnected)
            defresp.callback('yes')
        else:
            defresp.errback('no')

