
from Tkinter import *
from twisted.python import log

from shtoom.ui.base import ShtoomBaseUI
from shtoom.exceptions import CallRejected

#class AuthDialog(Dialog):
#
#    def __init__(self, prompt, parent):
#        
#        Dialog.__init(self, parent, 'Authentication Required')
        

class ShtoomMainWindow(ShtoomBaseUI):
    def __init__(self):
        self.cookie = False

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
        self._prefButton = Button(self._top2, text="Prefs",
                                  command=self.prefButton_clicked)
        self._prefButton.pack(side=RIGHT)

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
        deferred = self.app.placeCall(sipURL)
        deferred.addCallbacks(self.callConnected, self.callDisconnected).addErrback(log.err)

    def callConnected(self, cookie):
        self.cookie = cookie
        self._hangupButton.config(state=NORMAL)

    def callDisconnected(self, cookie, message):
        self.errorMessage("call ended %s"%message)
        self._hangupButton.config(state=DISABLED)
        self._callButton.config(state=NORMAL)
        self.cookie = None

    def hangupButton_clicked(self):
        self.app.dropCall(self.cookie)
        self._callButton.config(state=NORMAL)
        self._hangupButton.config(state=DISABLED)
        self.cookie = False

    def shutdown(self):
        # XXX Hang up any calls
        from twisted.internet import reactor
        reactor.stop()
        self.main.quit()

    def getAuth(self, message):
        from tkSimpleDialog import askstring
        from twisted.internet import defer
        answer = askstring('Authentication Required', message+'\nEnter as user,passwd')
        if answer:
            user, passwd = answer.split(',',1)
            user, passwd = user.strip(), passwd.strip()
        else:
            user, passwd = None, None
        return defer.succeed((user, passwd))

    def incomingCall(self, description, cookie, defresp):
        import tkMessageBox
        answer = tkMessageBox.askyesno("Shtoom", "Incoming Call: %s\nAnswer?"%description)
        if answer:
            self.cookie = cookie
            self._callButton.config(state=DISABLED)
            defresp.callback('yes')
        else:
            defresp.errback(CallRejected)

    def prefButton_clicked(self):
        from prefs import PreferencesDialog
        self._p = PreferencesDialog(self.main, self, self.app.getOptions())

    def updateOptions(self, od):
        self.app.updateOptions(od)
