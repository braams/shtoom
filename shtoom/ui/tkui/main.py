
from Tkinter import *
from twisted.python import log

from shtoom.ui.base import ShtoomBaseUI
from shtoom.exceptions import CallRejected

#class AuthDialog(Dialog):
#
#    def __init__(self, prompt, parent):
#        
#        Dialog.__init(self, parent, 'Authentication Required')
        
from shtoom.ui.logo import b64logo

class ShtoomMainWindow(ShtoomBaseUI):
    def __init__(self):
        self.cookie = False

        self.main = Tk(className='shtoom')
        # also do hangup, shutdown reactor, &c
        self.main.protocol("WM_DELETE_WINDOW", self.shutdown)
        self._top1 = Frame(self.main)
        self._top1.grid(row=1, column=1, sticky=NW)
        self._label1 = Label(self._top1, text='SIP:')
        self._label1.grid(row=1,column=1, sticky=W)
        self._urlentry = Entry(self._top1, width=60)
        self._urlentry.grid(row=1, column=2, columnspan=4, sticky=W)
        self._urlentry.bind('<Return>', self.callButton_clicked)
        self._urlentry.focus_set()
        self._prefButton = Button(self._top1, text="Prefs",
                                  command=self.prefButton_clicked)
        self._prefButton.grid(row=1, column=6, sticky=E)
        self._img = PhotoImage(data=b64logo)
        self._logo = Label(self._top1, image=self._img)
        self._logo.grid(row=1, column=7, rowspan=2, sticky=NE)

        self._top3 = Frame(self._top1)
        self._callButton = Button(self._top3, text="Call",
                                  command=self.callButton_clicked)
        self._callButton.grid(row=1, column=1, sticky=NW) 
        self._hangupButton = Button(self._top3, text="Hang up",
                                    command=self.hangupButton_clicked,
                                    state=DISABLED)
        self._hangupButton.grid(row=1, column=2, sticky=NW) 
        self._registerButton = Button(self._top3, text="Register",
                                  command=self.registerButton_clicked)
        self._registerButton.grid(row=1, column=3, sticky=NW) 
        self._top3.grid(row=2,column=1,columnspan=2, sticky=NW)
        self._statusF = Frame(self._top1)
        self._statusL = Label(self._statusF, text="Status:")
        self._statusL.grid(column=1,row=1,sticky=W)
        self._statusW = Label(self._statusF, text="")
        self._statusW.grid(column=2,row=1,sticky=W)
        self._statusF.grid(row=2, column=4, columnspan=1, sticky=W)

        self._top2 = Frame(self.main)
        self._buttonF = Frame(self._top2)
        self._dtmfbuttons = {}
        for row, dtmfs in enumerate(( ( '1', '2', '3' ), 
                                      ( '4', '5', '6' ), 
                                      ( '7', '8', '9' ), 
                                      ( '*', '0', '#' ))):
            for col, dtmf in enumerate(dtmfs):
                button = Button(self._buttonF, text=dtmf, padx=4, pady=2)
                button.bind('<1>', lambda e, d=dtmf: self.startDTMF(d) )
                button.bind('<ButtonRelease-1>', lambda e, d=dtmf: self.stopDTMF(d) )
                button.grid(row=row+1, column=col+1, sticky=NW)
                self._dtmfbuttons[dtmf] = button
        self._buttonF.grid(row=1,column=1, sticky=NW)
        self._debugText = Text(self._top2, width=72, height=7, wrap='char')
        self._debugText.grid(row=1,column=2, sticky=NW)
        self._top2.grid(row=3,column=1, columnspan=6,sticky=NW)
        

    def startDTMF(self, key):
        if self.cookie:
            self.app.startDTMF(self.cookie, key)

    def stopDTMF(self, key):
        if self.cookie:
            self.app.stopDTMF(self.cookie, key)

    def getMain(self):
        return self.main

    def debugMessage(self, msg):
        self._debugText.insert('end', msg+'\n')
        self._debugText.yview('end')

    def statusMessage(self, msg):
        self._statusW.configure(text=msg)

    def errorMessage(self, message, exc=None):
        log.msg("error %s"%(message))

    def callButton_clicked(self, evt=None):
        sipURL = self._urlentry.get()
        if not sipURL.startswith('sip:'):
            log.msg("Invalid SIP url %s"%(sipURL))
            return
        self._callButton.config(state=DISABLED)
        deferred = self.app.placeCall(sipURL)
        deferred.addCallbacks(self.callStarted, self.callFailed).addErrback(log.err)

    def registerButton_clicked(self, evt=None):
        self.app.register()

    def callConnected(self, cookie):
        pass

    def callDisconnected(self, e):
        self.statusMessage("Call disconnected: %r"%(e))

    def callStarted(self, cookie):
        self.cookie = cookie
        self._hangupButton.config(state=NORMAL)

    def callFailed(self, cookie, message):
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

    def getLogger(self):
        return Logger(self._debugText)

class Logger:
    def __init__(self, textwidget):
        self._t = textwidget
    def flush(self):
        pass
    def write(self, text):
        self._t.insert('end', msg+'\n')
        self._t.yview('end')

